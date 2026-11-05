<?php
class GC37Value {
    public $child = null;
}
class GC37Child {
    public function __destruct() {
        echo 'C|', $GLOBALS['gc37Watch']->get() === null ? 'N' : 'L', '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC37Value;
$map[$key] = $value;
$value->child = new GC37Child;
$GLOBALS['gc37Watch'] = WeakReference::create($value);
unset($value);
echo 'B|';
unset($key);
echo 'A|', $GLOBALS['gc37Watch']->get() === null ? 'N' : 'L', '|';
