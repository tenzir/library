# Invalid arguments and a rejected token stop the run before any write. The
# test prints only the error messages, without their source locations, so
# that edits of the operator don't change the baseline.

# `TENZIR_BINARY` ends with `run` unless the caller set it without.
case $TENZIR_BINARY in
  *" run") tenzir=$TENZIR_BINARY ;;
  *) tenzir="$TENZIR_BINARY run" ;;
esac
errors() {
  $tenzir --package-dirs="$TENZIR_TEST_ROOT" "$1" 2>&1 | sed -n 's/^[Ee]rror: //p'
}

# An unknown indicator type.
errors '
from {email: "attacker@example.com"}
harfanglab::ioc::sync env("HARFANGLAB_URL"), token=env("HARFANGLAB_TOKEN"),
  source="tenzir-test-iocs", type="email", value=email
'

# Blocking states need allow_blocking=true.
errors '
from {domain: "c2.example.net"}
harfanglab::ioc::sync env("HARFANGLAB_URL"), token=env("HARFANGLAB_TOKEN"),
  source="tenzir-test-iocs", type="domain", value=domain, state="block"
'

# The prune share is a fraction.
errors '
from {domain: "c2.example.net"}
harfanglab::ioc::sync env("HARFANGLAB_URL"), token=env("HARFANGLAB_TOKEN"),
  source="tenzir-test-iocs", type="domain", value=domain, prune=true,
  max_prune_share=10.0
'

# A rejected token.
errors '
from {domain: "c2.example.net"}
harfanglab::ioc::sync env("HARFANGLAB_URL"), token="wrong-token",
  source="tenzir-test-iocs", type="domain", value=domain
'
