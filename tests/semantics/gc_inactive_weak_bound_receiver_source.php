<?php
class GcWeakOrderChild30 {
    public function __destruct() { echo 'CHILD|'; }
}
class GcWeakBoundParent30 {
    public $child;
    public function handler($level, $message) { return false; }
}
class GcWeakOrderLate30 {
    public $parent;
    public $weak;
    public function __destruct() {
        $GLOBALS['savedParent'] = $this->parent;
        $GLOBALS['savedWeak'] = $this->weak;
        echo 'D1|';
        $this->parent->child = new GcWeakOrderChild30;
        echo $this->weak->get() === $this->parent ? 'L|' : 'BAD|';
        echo 'D2|';
    }
}
$filler = new stdClass;
$parent = new GcWeakBoundParent30;
$parent->child = null;
$weak = WeakReference::create($parent);
unset($filler);
set_error_handler($parent->handler(...));
ob_start(static function ($bytes, $phase) use ($parent, $weak) {
    $late = new GcWeakOrderLate30;
    $late->parent = $parent;
    $late->weak = $weak;
    register_shutdown_function(static function () {}, $late);
    return 'F' . $bytes;
});
echo 'X|';
