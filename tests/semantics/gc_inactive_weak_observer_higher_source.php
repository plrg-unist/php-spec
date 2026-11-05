<?php
class GcWeakOrderChild30 {
    public function __destruct() { echo 'CHILD|'; }
}
class GcWeakOrderLate30 {
    public function __destruct() {
        global $parent, $weak;
        echo 'D1|';
        $parent->child = new GcWeakOrderChild30;
        echo $weak->get() === $parent ? 'L|' : 'BAD|';
        echo 'D2|';
    }
}
$filler = new stdClass;
$parent = new stdClass;
$parent->child = null;
$weak = WeakReference::create($parent);
unset($filler);
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcWeakOrderLate30);
    return 'F' . $bytes;
});
echo 'X|';
