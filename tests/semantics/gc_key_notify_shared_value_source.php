<?php
class GcNotifySharedA32 { public function __destruct() { echo "A|"; } }
class GcNotifySharedField32 { public function __destruct() { echo "C|"; } }
class GcNotifySharedSetup32 {
    public function __destruct() {
        echo "D1|";
        $map = new WeakMap;
        $keyB = new stdClass;
        $keyA = new stdClass;
        $shared = new GcNotifySharedA32;
        $map[$keyA] = $shared;
        $map[$keyB] = $shared;
        $keyA->child = new GcNotifySharedField32;
        $GLOBALS['gcNotifySharedMap32'] = $map;
        $GLOBALS['gcNotifySharedKeyB32'] = $keyB;
        $GLOBALS['gcNotifySharedKeyA32'] = $keyA;
        echo "D2|";
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcNotifySharedSetup32);
    return "F" . $bytes;
});
echo "X|";
