<?php
class GC39Value { public $child = null; }
class GC39Child {
    public function __destruct() {
        global $valueWatch, $mapWatch, $keyWatch;
        echo 'C|', (int) ($valueWatch->get() === null), '|',
             (int) ($mapWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC39Value;
$map[$key] = $value;
$child = new GC39Child;
$value->child = $child;
$valueWatch = WeakReference::create($value);
$mapWatch = WeakReference::create($map);
$keyWatch = WeakReference::create($key);
unset($value);
echo 'B|';
unset($map);
echo 'A|', (int) ($valueWatch->get() === null), '|',
     (int) ($mapWatch->get() === null), '|',
     (int) ($keyWatch->get() !== null), '|';
unset($child);
echo 'X|';
