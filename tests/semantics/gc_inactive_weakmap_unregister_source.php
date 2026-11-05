<?php
class GcMapHolder31 {
    public $child;
}
class GcMapUnregisterLate31 {
    public function __destruct() {
        echo 'D1|';
        $keyA = new stdClass;
        $keyB = new stdClass;
        $holder = new GcMapHolder31;
        $holder->child = null;
        $map = new WeakMap;
        $map[$keyA] = $holder;
        $map[$keyB] = 17;
        $holder->child = $keyB;
        $GLOBALS['savedMap'] = $map;
        $GLOBALS['savedKeyA'] = $keyA;
        echo $holder->child === $keyB ? 'linked|' : 'BAD|';
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcMapUnregisterLate31);
    return 'F' . $bytes;
});
echo 'X|';
