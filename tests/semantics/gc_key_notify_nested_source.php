<?php
class GcNotifyHolder32 { public $keyB; }
class GcNotifyFatal32 { public function __destruct() { echo "B|"; } }
class GcNotifyField32 { public function __destruct() { echo "C|"; } }
class GcNotifySetup32 {
    public function __destruct() {
        echo "D1|";
        $map = new WeakMap;
        $holder = new GcNotifyHolder32;
        $keyB = new stdClass;
        $keyA = new stdClass;
        $map[$keyA] = $holder;
        $map[$keyB] = new GcNotifyFatal32;
        $holder->keyB = $keyB;
        $keyA->child = new GcNotifyField32;
        $GLOBALS['gcNotifyMap32'] = $map;
        $GLOBALS['gcNotifyKeyA32'] = $keyA;
        echo "D2|";
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcNotifySetup32);
    return "F" . $bytes;
});
echo "X|";
