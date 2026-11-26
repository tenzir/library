# A listing that returns fewer IOCs than it counts stops the run before any
# write, even with prune=true. The test prints only the error message,
# without its source location.

# `TENZIR_BINARY` ends with `run` unless the caller set it without.
case $TENZIR_BINARY in
  *" run") tenzir=$TENZIR_BINARY ;;
  *) tenzir="$TENZIR_BINARY run" ;;
esac
$tenzir --package-dirs="$TENZIR_TEST_ROOT" '
from {domain: "ioc-0.example.net"}, {domain: "ioc-1400.example.net"}
harfanglab::ioc::sync env("HARFANGLAB_URL"), token=env("HARFANGLAB_TOKEN"),
  source="tenzir-fault-truncated", type="domain", value=domain, prune=true,
  max_prune_share=1.0
' 2>&1 | sed -n 's/^[Ee]rror: //p'
