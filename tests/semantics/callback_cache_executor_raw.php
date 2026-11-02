<?php
class ShutdownRawInvoker {
    public function __invoke() {
        $GLOBALS["calls"]++;
        echo "B:", $GLOBALS["weak"]->get() === $this, ":", $GLOBALS["calls"] === 1, ";";
    }
    public function __destruct() { echo "D:", $GLOBALS["calls"] === 1, ";"; }
}
function inspect_shutdown_raw() { echo "S:", $GLOBALS["weak"]->get() !== null, ":", $GLOBALS["calls"] === 1, ";"; }
$calls = 0; $owner = new ShutdownRawInvoker; $weak = WeakReference::create($owner);
register_shutdown_function($owner); register_shutdown_function("inspect_shutdown_raw");
$owner = null; echo "P:", $weak->get() !== null, ";";
