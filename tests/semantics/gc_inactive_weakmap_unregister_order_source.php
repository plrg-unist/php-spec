<?php
class GcMapOrderHolder31 {
    public $child;
    public $tail;
}
class GcMapLaterValue31 {
    public function __destruct() { echo 'LATER|'; }
}
class GcMapTailValue31 {
    public function __destruct() { echo 'TAIL|'; }
}
class GcMapUnregisterOrderLate31 {
    public function __destruct() {
        echo 'D1|';
        $keyA = new stdClass;
        $keyB = new stdClass;
        $holder = new GcMapOrderHolder31;
        $holder->child = null;
        $holder->tail = null;
        $later = new GcMapLaterValue31;
        $map = new WeakMap;
        $map[$keyA] = $holder;
        $map[$keyB] = $later;
        $holder->child = $keyB;
        $holder->tail = new GcMapTailValue31;
        $GLOBALS['savedOrderMap'] = $map;
        $GLOBALS['savedOrderKeyA'] = $keyA;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcMapUnregisterOrderLate31);
    return 'F' . $bytes;
});
echo 'X|';
