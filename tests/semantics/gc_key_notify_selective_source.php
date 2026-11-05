<?php
class GcNotifyHeldA32 { public function __destruct() { echo "A|"; } }
class GcNotifySpareB32 { public function __destruct() { echo "B|"; } }
class GcNotifyFieldC32 { public function __destruct() { echo "C|"; } }
class GcNotifySetup32 {
    public function __destruct() {
        echo "D1|";
        $map = new WeakMap;
        $keyB = new stdClass;
        $keyA = new stdClass;
        $a = new GcNotifyHeldA32;
        $map[$keyA] = $a;
        $map[$keyB] = new GcNotifySpareB32;
        $keyA->child = new GcNotifyFieldC32;
        $GLOBALS['gcNotifyMap32'] = $map;
        $GLOBALS['gcNotifyKeyB32'] = $keyB;
        $GLOBALS['gcNotifyKeyA32'] = $keyA;
        $GLOBALS['gcNotifyHeldA32'] = $a;
        echo "D2|";
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcNotifySetup32);
    return "F" . $bytes;
});
echo "X|";
