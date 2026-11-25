"""Write a pcap with invented traffic of a small fictional office.

The traffic uses documentation and private addresses and `.example` names
only. The same script always writes the same bytes.

    python3 -I make_traffic.py traffic.pcap
"""

import hashlib
import ipaddress
import struct
import sys

START = 1_767_261_600  # 2026-01-01T10:00:00Z
GATEWAY, DNS, MAIL, FILES = "10.20.0.1", "10.20.0.53", "10.20.0.25", "10.20.0.40"
WEB = {
    "www.shop.example": "192.0.2.10",
    "updates.vendor.example": "192.0.2.20",
    "intranet.office.example": "10.20.0.80",
    "mail.office.example": MAIL,
    "cdn.assets.example": "198.51.100.30",
    "login.cloud.example": "198.51.100.40",
    "telemetry.badsite.example": "203.0.113.66",
}
CLIENTS = [f"10.20.1.{host}" for host in (11, 12, 13, 14)]


def mac(address):
    return b"\x02\x00" + ipaddress.ip_address(address).packed


def checksum(data):
    data += b"\0" * (len(data) % 2)
    total = sum(struct.unpack(f">{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


def noise(label, length):
    """Deterministic stand-in for random bytes."""
    out, block = b"", 0
    while len(out) < length:
        out += hashlib.sha256(f"{label}:{block}".encode()).digest()
        block += 1
    return out[:length]


class Capture:
    def __init__(self):
        self.packets = []
        self.ident = 0

    def ip(self, at, src, dst, proto, payload):
        self.ident += 1
        header = struct.pack(
            ">BBHHHBBH4s4s", 0x45, 0, 20 + len(payload), self.ident & 0xFFFF, 0x4000,
            64, proto, 0, ipaddress.ip_address(src).packed, ipaddress.ip_address(dst).packed)
        header = header[:10] + struct.pack(">H", checksum(header)) + header[12:]
        target = b"\xff" * 6 if dst == "255.255.255.255" else mac(dst)
        self.packets.append((at, target + mac(src) + b"\x08\x00" + header + payload))

    def segment(self, src, dst, proto, data):
        pseudo = ipaddress.ip_address(src).packed + ipaddress.ip_address(dst).packed
        return checksum(pseudo + struct.pack(">BBH", 0, proto, len(data)) + data)

    def udp(self, at, src, sport, dst, dport, payload):
        data = struct.pack(">HHHH", sport, dport, 8 + len(payload), 0) + payload
        data = data[:6] + struct.pack(">H", self.segment(src, dst, 17, data) or 0xFFFF) + data[8:]
        self.ip(at, src, dst, 17, data)

    def tcp(self, at, src, sport, dst, dport, seq, ack, flags, payload=b""):
        data = struct.pack(">HHIIBBHHH", sport, dport, seq, ack, 0x50, flags, 64240, 0, 0) + payload
        data = data[:16] + struct.pack(">H", self.segment(src, dst, 6, data)) + data[18:]
        self.ip(at, src, dst, 6, data)

    def session(self, at, src, sport, dst, dport, exchanges):
        """A TCP connection. `exchanges` holds (from_client, payload) pairs."""
        c = int.from_bytes(noise(f"isn{src}{sport}", 4), "big") >> 1
        s = int.from_bytes(noise(f"isn{dst}{sport}", 4), "big") >> 1
        self.tcp(at, src, sport, dst, dport, c, 0, 0x02)
        self.tcp(at + 0.012, dst, dport, src, sport, s, c + 1, 0x12)
        self.tcp(at + 0.0125, src, sport, dst, dport, c + 1, s + 1, 0x10)
        c, s, at = c + 1, s + 1, at + 0.015
        for client, payload in exchanges:
            for i in range(0, len(payload), 1400):
                part = payload[i:i + 1400]
                if client:
                    self.tcp(at, src, sport, dst, dport, c, s, 0x18, part)
                    c += len(part)
                    self.tcp(at + 0.006, dst, dport, src, sport, s, c, 0x10)
                else:
                    self.tcp(at, dst, dport, src, sport, s, c, 0x18, part)
                    s += len(part)
                    self.tcp(at + 0.006, src, sport, dst, dport, c, s, 0x10)
                at += 0.011
            at += 0.02
        self.tcp(at, src, sport, dst, dport, c, s, 0x11)
        self.tcp(at + 0.007, dst, dport, src, sport, s, c + 1, 0x11)
        self.tcp(at + 0.008, src, sport, dst, dport, c + 1, s + 1, 0x10)
        return at + 0.01

    def save(self, path):
        with open(path, "wb") as out:
            out.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
            for at, frame in sorted(self.packets, key=lambda p: p[0]):
                micros = round(at * 1_000_000)
                out.write(struct.pack("<IIII", micros // 1_000_000, micros % 1_000_000,
                                      len(frame), len(frame)) + frame)


def dns_name(name):
    return b"".join(bytes([len(p)]) + p.encode() for p in name.split(".")) + b"\0"


def lookup(cap, at, client, port, name, kind=1):
    """A DNS query with its answer, or NXDOMAIN for unknown names."""
    ident = int.from_bytes(noise(f"dns{client}{port}{name}", 2), "big")
    question = dns_name(name) + struct.pack(">HH", kind, 1)
    cap.udp(at, client, port, DNS, 53, struct.pack(">HHHHHH", ident, 0x0100, 1, 0, 0, 0) + question)
    address = WEB.get(name) if kind == 1 else None
    answer = b""
    if address:
        answer = b"\xc0\x0c" + struct.pack(">HHIH", 1, 1, 300, 4) + ipaddress.ip_address(address).packed
    flags = 0x8180 if address else 0x8183
    cap.udp(at + 0.018, DNS, 53, client, port,
            struct.pack(">HHHHHH", ident, flags, 1, 1 if address else 0, 0, 0) + question + answer)


def http(method, host, path, agent, status, kind, body, request=b""):
    head = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {agent}\r\nAccept: */*\r\n"
    if request:
        head += f"Content-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(request)}\r\n"
    reply = f"HTTP/1.1 {status}\r\nContent-Type: {kind}\r\nContent-Length: {len(body)}\r\nServer: demo\r\n\r\n"
    return [(True, head.encode() + b"\r\n" + request), (False, reply.encode() + body)]


def tls(label, host):
    """A TLS 1.3 handshake with opaque application data."""
    def record(kind, data, version=0x0303):
        return struct.pack(">BHH", kind, version, len(data)) + data

    def extension(number, data):
        return struct.pack(">HH", number, len(data)) + data

    name = host.encode()
    offered = (
        extension(0, struct.pack(">HBH", len(name) + 3, 0, len(name)) + name)
        + extension(10, struct.pack(">HH", 2, 29))
        + extension(13, struct.pack(">HHH", 4, 0x0403, 0x0804))
        + extension(16, struct.pack(">HB", 3, 2) + b"h2")
        + extension(43, b"\x02\x03\x04")
        + extension(51, struct.pack(">HHH", 36, 29, 32) + noise(label + "ck", 32)))
    hello = (struct.pack(">H", 0x0303) + noise(label + "cr", 32) + b"\x20" + noise(label + "sid", 32)
             + struct.pack(">HHHH", 6, 0x1301, 0x1302, 0x1303) + b"\x01\x00"
             + struct.pack(">H", len(offered)) + offered)
    chosen = extension(43, b"\x03\x04") + extension(51, struct.pack(">HH", 29, 32) + noise(label + "sk", 32))
    reply = (struct.pack(">H", 0x0303) + noise(label + "sr", 32) + b"\x20" + noise(label + "sid", 32)
             + struct.pack(">HB", 0x1301, 0) + struct.pack(">H", len(chosen)) + chosen)
    ccs = record(20, b"\x01")
    return [
        (True, record(22, b"\x01" + len(hello).to_bytes(3, "big") + hello, 0x0301)),
        (False, record(22, b"\x02" + len(reply).to_bytes(3, "big") + reply) + ccs
         + record(23, noise(label + "enc", 980))),
        (True, ccs + record(23, noise(label + "fin", 53)) + record(23, noise(label + "req", 420))),
        (False, record(23, noise(label + "res", 2600))),
    ]


def smtp(sender, recipient, subject):
    body = (f"From: {sender}\r\nTo: {recipient}\r\nSubject: {subject}\r\n"
            f"Message-ID: <{noise(subject, 8).hex()}@office.example>\r\n\r\nSee you there.\r\n.\r\n")
    return [
        (False, b"220 mail.office.example ESMTP\r\n"), (True, b"EHLO client.office.example\r\n"),
        (False, b"250 mail.office.example\r\n"), (True, f"MAIL FROM:<{sender}>\r\n".encode()),
        (False, b"250 OK\r\n"), (True, f"RCPT TO:<{recipient}>\r\n".encode()),
        (False, b"250 OK\r\n"), (True, b"DATA\r\n"), (False, b"354 Go ahead\r\n"),
        (True, body.encode()), (False, b"250 Queued\r\n"), (True, b"QUIT\r\n"), (False, b"221 Bye\r\n"),
    ]


def dhcp(cap, at, client, hostname):
    ident = noise("dhcp" + client, 4)

    def message(op, kind, address, options):
        packed = ipaddress.ip_address(address).packed
        return (struct.pack(">BBBB", op, 1, 6, 0) + ident + b"\0" * 4 + b"\0" * 4
                + (packed if op == 2 else b"\0" * 4) + b"\0" * 8 + mac(client) + b"\0" * 10
                + b"\0" * 192 + b"\x63\x82\x53\x63" + b"\x35\x01" + bytes([kind]) + options + b"\xff")

    name = b"\x0c" + bytes([len(hostname)]) + hostname.encode()
    wanted = b"\x32\x04" + ipaddress.ip_address(client).packed
    lease = (b"\x33\x04" + struct.pack(">I", 3600) + b"\x01\x04\xff\xff\x00\x00"
             + b"\x36\x04" + ipaddress.ip_address(GATEWAY).packed)
    cap.udp(at, "0.0.0.0", 68, "255.255.255.255", 67, message(1, 3, client, wanted + name))
    cap.udp(at + 0.03, GATEWAY, 67, client, 68, message(2, 5, client, lease))


def main(path):
    cap, agent = Capture(), "Mozilla/5.0 (X11; Linux x86_64) DemoBrowser/1.0"
    port = 40_000

    def next_port():
        nonlocal port
        port += 7
        return port

    def browse(at, client, host, path="/", secure=False, **kwargs):
        lookup(cap, at, client, next_port(), host)
        source = next_port()
        if secure:
            return cap.session(at + 0.05, client, source, WEB[host], 443, tls(f"{client}{source}", host))
        page = kwargs.pop("body", b"<html><body>" + b"demo " * 60 + b"</body></html>")
        return cap.session(at + 0.05, client, source, WEB[host], 80, http(
            kwargs.pop("method", "GET"), host, path, kwargs.pop("agent", agent),
            kwargs.pop("status", "200 OK"), kwargs.pop("kind", "text/html"), page, **kwargs))

    for i, client in enumerate(CLIENTS):
        dhcp(cap, START + 2 + i * 41.3, client, f"desktop-{i + 1}")
    hosts = ["www.shop.example", "cdn.assets.example", "login.cloud.example",
             "intranet.office.example", "updates.vendor.example"]
    for step in range(24):
        client = CLIENTS[step % 4]
        host = hosts[(step * 3 + step // 4) % 5]
        at = START + 5 + step * 12.1 + (step % 3) * 2.7
        if step % 3 == 0:
            browse(at, client, host, f"/item/{step}")
        else:
            browse(at, client, host, secure=True)
    for i, (sender, recipient, subject) in enumerate([
            ("ada@office.example", "ben@office.example", "Lunch on Friday"),
            ("ben@office.example", "ada@office.example", "Re: Lunch on Friday")]):
        cap.session(START + 60 + i * 110, CLIENTS[i], next_port(), MAIL, 25, smtp(sender, recipient, subject))
    # A workstation contacts a suspicious host, repeatedly and in clear text.
    for beat in range(6):
        at = START + 90 + beat * 30.5
        browse(at, CLIENTS[2], "telemetry.badsite.example", "/gate.php", method="POST",
               agent="demo-beacon/0.1", body=b"ok", kind="text/plain",
               request=b"id=" + noise(f"beat{beat}", 24).hex().encode())
    browse(START + 80, CLIENTS[2], "www.shop.example", "/download/invoice.exe",
           kind="application/x-msdownload", body=b"MZ" + noise("exe", 3000))
    browse(START + 150, CLIENTS[3], "intranet.office.example", "/../../etc/passwd", status="403 Forbidden", body=b"denied")
    lookup(cap, START + 120, CLIENTS[0], next_port(), "printer.office.example")
    lookup(cap, START + 200, CLIENTS[2], next_port(), "a8f3k2.badsite.example")
    # A port scan against the file server; every port is closed.
    for i, target in enumerate((21, 22, 23, 80, 139, 443, 445, 1433, 3306, 3389, 5900, 8080)):
        at, source = START + 230 + i * 0.4, next_port()
        cap.tcp(at, CLIENTS[2], source, FILES, target, 1000 + i, 0, 0x02)
        cap.tcp(at + 0.004, FILES, target, CLIENTS[2], source, 0, 1001 + i, 0x14)
    ssh = [(False, b"SSH-2.0-DemoServer_1.0\r\n"), (True, b"SSH-2.0-DemoClient_1.0\r\n")]
    cap.session(START + 262, CLIENTS[0], next_port(), FILES, 22, ssh)
    cap.save(path)


if __name__ == "__main__":
    main(sys.argv[1])
