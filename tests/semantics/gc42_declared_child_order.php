<?php
class GC42Value {
    public $first = null;
    public $scalar = null;
    public $last = null;
}
class GC42Leaf {}
class GC42FirstChild {
    public function __destruct() {
        global $mapWatch, $valueWatch, $leafWatch, $lastWatch;
        echo 'F|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|',
             (int) ($lastWatch->get() !== null), '|';
    }
}
class GC42LastChild {
    public function __destruct() {
        global $mapWatch, $valueWatch, $leafWatch, $firstWatch;
        echo 'L|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|',
             (int) ($firstWatch->get() === null), '|';
    }
}
$map = new WeakMap;
$valueKey = new stdClass;
$leafKey = new stdClass;
$value = new GC42Value;
$leaf = new GC42Leaf;
$map[$valueKey] = $value;
$map[$leafKey] = $leaf;
$value->last = new GC42LastChild;
$value->first = new GC42FirstChild;
$value->scalar = 1.25;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$leafWatch = WeakReference::create($leaf);
$firstWatch = WeakReference::create($value->first);
$lastWatch = WeakReference::create($value->last);
echo 'B|', $value->scalar, '|';
unset($value, $leaf);
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($valueWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|',
     (int) ($firstWatch->get() === null), '|',
     (int) ($lastWatch->get() === null), '|';
