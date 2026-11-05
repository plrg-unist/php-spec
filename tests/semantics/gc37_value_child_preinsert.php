<?php
class GC37ValuePre {
    public $child = null;
}
class GC37ChildPre {
    public function __destruct() {
        echo 'C|', $GLOBALS['gc37Watch']->get() === null ? 'N' : 'L', '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC37ValuePre;
$value->child = new GC37ChildPre;
$map[$key] = $value;
$GLOBALS['gc37Watch'] = WeakReference::create($value);
unset($value);
echo 'B|';
unset($key);
echo 'A|', $GLOBALS['gc37Watch']->get() === null ? 'N' : 'L', '|';
