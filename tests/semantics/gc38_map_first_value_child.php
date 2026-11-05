<?php
class GC38Value {
    public $child = null;
}
class GC38Child {
    public function __destruct() {
        echo 'C|', $GLOBALS['gc38ValueWatch']->get() === null ? 'VN' : 'VL', '|';
        echo $GLOBALS['gc38MapWatch']->get() === null ? 'MN' : 'ML', '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC38Value;
$value->child = new GC38Child;
$map[$key] = $value;
$GLOBALS['gc38ValueWatch'] = WeakReference::create($value);
$GLOBALS['gc38MapWatch'] = WeakReference::create($map);
unset($value);
echo 'B|';
unset($map);
echo 'A|', $GLOBALS['gc38ValueWatch']->get() === null ? 'VN' : 'VL', '|';
echo $GLOBALS['gc38MapWatch']->get() === null ? 'MN' : 'ML', '|';
echo $key instanceof stdClass ? 'KL|' : 'KN|';
