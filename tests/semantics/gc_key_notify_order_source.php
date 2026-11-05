<?php
class GcNotifyHolder32 { public $child = null; }
class GcNotifyFirst32 { public function __destruct() { echo "A|"; } }
class GcNotifySecond32 { public function __destruct() { echo "B|"; } }
class GcNotifyLate32 {
    public function __destruct() {
        echo "D1|";
        $first = new WeakMap;
        $second = new WeakMap;
        $left = new GcNotifyHolder32;
        $right = new GcNotifyHolder32;
        $key = new stdClass;
        $second[$key] = $right;
        $first[$key] = $left;
        $left->child = new GcNotifyFirst32;
        $right->child = new GcNotifySecond32;
        $GLOBALS['notifyFirst32'] = $first;
        $GLOBALS['notifySecond32'] = $second;
        $GLOBALS['notifyKey32'] = $key;
        echo "D2|";
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcNotifyLate32);
    return "F" . $bytes;
});
echo "X|";
