# A failing listing stops the run before any IOC write. The test prints only
# the error message, without its source location.

# `TENZIR_BINARY` ends with `run` unless the caller set it without.
case $TENZIR_BINARY in
  *" run") tenzir=$TENZIR_BINARY ;;
  *) tenzir="$TENZIR_BINARY run" ;;
esac
$tenzir --package-dirs="$TENZIR_TEST_ROOT" '
from {domain: "a.example.com"}
harfanglab::ioc::sync env("HARFANGLAB_URL"), token=env("HARFANGLAB_TOKEN"),
  source="tenzir-fault-listing", type="domain", value=domain
' 2>&1 | sed -n 's/^[Ee]rror: //p'
