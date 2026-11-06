<?php
function refCopyTarget70() {}
class RefCopyParent70 {
    public $quiet = 17;
    public function __destruct() { echo 'P|', $this->quiet, '|'; }
}
class RefCopyOldName70 {
    public function __destruct() {
        global $name, $watch;
        $name = new RefCopyParent70;
        $watch = WeakReference::create($name);
        echo 'O|';
    }
}
$watch = null;
$name = new RefCopyOldName70;
echo 'B|';
$ok = is_callable('refCopyTarget70', false, $name);
echo 'N|', $ok, '|', $name, '|';
$parent = $watch->get();
$ref = 17;
$parent->quiet =& $ref;
unset($parent);
$source = [&$ref];
unset($ref);
$copy = $source;
$copy[0] = 23;
echo 'V|', $source[0], '|', $copy[0], '|', $watch->get()->quiet, '|';
unset($source, $copy, $name);
echo 'E|', $watch->get() !== null, '|';
