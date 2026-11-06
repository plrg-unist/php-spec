<?php
function rcGraphTarget69() {}
class RcGraphParent69 {
    public $child;
    public $quiet = 17;
    public function __destruct() {
        global $childWatch;
        echo 'P|', $childWatch->get() !== null, '|';
    }
}
class RcGraphChild69 {
    public function __destruct() {
        global $parentWatch;
        echo 'C|', $parentWatch->get() !== null, '|';
    }
}
class RcGraphOldName69 {
    public function __destruct() {
        global $name, $parentWatch, $childWatch;
        $name = new RcGraphParent69;
        $child = new RcGraphChild69;
        $name->child = $child;
        $parentWatch = WeakReference::create($name);
        $childWatch = WeakReference::create($child);
        unset($child);
        echo 'O|';
    }
}
$parentWatch = $childWatch = null;
$name = new RcGraphOldName69;
echo 'B|';
$ok = is_callable('rcGraphTarget69', false, $name);
echo 'N|', $ok, '|', $name, '|', $parentWatch->get() !== null, '|', $childWatch->get() !== null, '|';
unset($name);
echo 'U|', $parentWatch->get() !== null, '|', $childWatch->get() !== null, '|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|', $parentWatch->get() !== null, '|', $childWatch->get() !== null, '|';
register_shutdown_function(function () {
    global $parentWatch, $childWatch;
    echo 'S|', $parentWatch->get() !== null, '|', $childWatch->get() !== null, '|';
});
echo 'E|';
