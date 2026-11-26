# A feed that suddenly holds one domain would disable 39 of 40 IOCs, more
# than the prune limit, so the run stops before any write. The test prints
# only the error message, without its source location.

# `TENZIR_BINARY` ends with `run` unless the caller set it without.
case $TENZIR_BINARY in
  *" run") tenzir=$TENZIR_BINARY ;;
  *) tenzir="$TENZIR_BINARY run" ;;
esac
$tenzir --package-dirs="$TENZIR_TEST_ROOT" '
from {domain: "guard-0.example.net"}
harfanglab::ioc::sync env("HARFANGLAB_URL"), token=env("HARFANGLAB_TOKEN"),
  source="tenzir-test-guard", type="domain", value=domain, prune=true
' 2>&1 | sed -n 's/^[Ee]rror: //p'
