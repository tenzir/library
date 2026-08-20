#!/usr/bin/env python3
"""Small real MCP stdio server used as a disposable harness test target."""
import json
import os
import sys

LOG = os.environ.get("HARNESS_CHECK_MCP_LOG")
if len(sys.argv) == 3 and sys.argv[1] == "--log":
    LOG = sys.argv[2]


def log_request(request):
    method = request.get("method")
    if LOG and method:
        with open(LOG, "a", encoding="utf-8") as handle:
            row = method
            if method == "tools/call":
                params = request.get("params", {})
                row += "\t" + str(params.get("name", ""))
                row += "\t" + str(params.get("arguments", {}).get("text", ""))
            handle.write(row + "\n")


def reply(request):
    method = request.get("method")
    log_request(request)
    request_id = request.get("id")
    if method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True},
                "prompts": {"listChanged": True},
            },
            "serverInfo": {"name": "harness-check", "version": "1.0.0"},
        }
    elif method == "tools/list":
        result = {
            "tools": [{
                "name": "harness_echo",
                "description": "Echo a harmless harness-check marker",
                "inputSchema": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
            }]
        }
    elif method == "tools/call":
        text = request.get("params", {}).get("arguments", {}).get("text", "")
        result = {"content": [{"type": "text", "text": text}]}
    elif method == "resources/list":
        result = {"resources": [{
            "uri": "harness-check://fixture/resource",
            "name": "harness-check-resource",
            "description": "Disposable MCP resource telemetry marker",
            "mimeType": "text/plain",
        }]}
    elif method == "resources/read":
        result = {"contents": [{
            "uri": "harness-check://fixture/resource",
            "mimeType": "text/plain",
            "text": "harness-check-resource-read",
        }]}
    elif method in ("resources/subscribe", "resources/unsubscribe"):
        result = {}
    elif method == "prompts/list":
        result = {"prompts": [{
            "name": "harness-check-prompt",
            "description": "Disposable MCP prompt telemetry marker",
            "arguments": [],
        }]}
    elif method == "prompts/get":
        result = {
            "description": "Disposable MCP prompt telemetry marker",
            "messages": [{
                "role": "user",
                "content": {"type": "text", "text": "harness-check-prompt-get"},
            }],
        }
    elif method == "notifications/initialized":
        # Exercise the server-to-client notification channel. A client that
        # reacts will usually issue another list request, which the log proves.
        for changed in ("tools", "resources", "prompts"):
            print(json.dumps({
                "jsonrpc": "2.0",
                "method": f"notifications/{changed}/list_changed",
            }), flush=True)
        return None
    elif method and method.startswith("notifications/"):
        return None
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"unknown method: {method}"},
        }
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


for line in sys.stdin:
    try:
        response = reply(json.loads(line))
        if response is not None:
            print(json.dumps(response), flush=True)
    except Exception as error:
        print(json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": str(error)},
        }), flush=True)
