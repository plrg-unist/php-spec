<?php
class GcNotifyPositionV32 { public function __destruct() { echo "V|"; } }
class GcNotifyPositionW32 { public function __destruct() { echo "W|"; } }
class GcNotifyPositionSetup32 {
    public function __destruct() {
        echo "D1|";
        $keyA = new stdClass;
        $keyB = new stdClass;
        $map = new WeakMap;
        $keyC = new stdClass;
        $v = new GcNotifyPositionV32;
        $w = new GcNotifyPositionW32;
        $map[$keyA] = $v;
        $map[$keyB] = $w;
        $map[$keyC] = $v;
        $GLOBALS['gcNotifyPositionKeyA32'] = $keyA;
        $GLOBALS['gcNotifyPositionKeyB32'] = $keyB;
        $GLOBALS['gcNotifyPositionMap32'] = $map;
        $GLOBALS['gcNotifyPositionKeyC32'] = $keyC;
        echo "D2|";
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcNotifyPositionSetup32);
    return "F" . $bytes;
});
echo "X|";
