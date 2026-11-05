<?php
class GC40Value { public $child = null; }
class GC40Leaf {}
class GC40Child {
    public function __destruct() {
        global $mapWatch, $firstWatch, $secondWatch, $firstKeyWatch, $secondKeyWatch;
        echo 'C|', (int) ($mapWatch->get() !== null), '|',
             (int) ($firstWatch->get() === null), '|',
             (int) ($secondWatch->get() !== null), '|',
             (int) ($firstKeyWatch->get() !== null), '|',
             (int) ($secondKeyWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$first = new GC40Value;
$second = new GC40Leaf;
$map[$firstKey] = $first;
$map[$secondKey] = $second;
$first->child = new GC40Child;
$mapWatch = WeakReference::create($map);
$firstWatch = WeakReference::create($first);
$secondWatch = WeakReference::create($second);
$firstKeyWatch = WeakReference::create($firstKey);
$secondKeyWatch = WeakReference::create($secondKey);
unset($first, $second);
echo 'B|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($firstWatch->get() === null), '|',
     (int) ($secondWatch->get() === null), '|',
     (int) ($firstKeyWatch->get() !== null), '|',
     (int) ($secondKeyWatch->get() !== null), '|';
