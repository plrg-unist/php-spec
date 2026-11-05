<?php
class GC41Value { public $child = null; }
class GC41Leaf {}
class GC41FirstChild {
    public function __destruct() {
        global $mapWatch, $firstWatch, $secondWatch, $thirdWatch, $fourthWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($firstWatch->get() !== null), '|',
             (int) ($secondWatch->get() !== null), '|',
             (int) ($thirdWatch->get() !== null), '|',
             (int) ($fourthWatch->get() !== null), '|';
    }
}
class GC41ThirdChild {
    public function __destruct() {
        global $mapWatch, $firstWatch, $secondWatch, $thirdWatch, $fourthWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($firstWatch->get() !== null), '|',
             (int) ($secondWatch->get() !== null), '|',
             (int) ($thirdWatch->get() !== null), '|',
             (int) ($fourthWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$thirdKey = new stdClass;
$fourthKey = new stdClass;
$first = new GC41Value;
$second = new GC41Leaf;
$third = new GC41Value;
$fourth = new GC41Leaf;
$map[$firstKey] = $first;
$map[$secondKey] = $second;
$map[$thirdKey] = $third;
$map[$fourthKey] = $fourth;
$first->child = new GC41FirstChild;
$third->child = new GC41ThirdChild;
$mapWatch = WeakReference::create($map);
$firstWatch = WeakReference::create($first);
$secondWatch = WeakReference::create($second);
$thirdWatch = WeakReference::create($third);
$fourthWatch = WeakReference::create($fourth);
unset($first, $second, $third, $fourth);
echo 'B|';
unset($map);
echo 'A|', (int) ($mapWatch->get() !== null), '|',
     (int) ($firstWatch->get() !== null), '|',
     (int) ($secondWatch->get() !== null), '|',
     (int) ($thirdWatch->get() !== null), '|',
     (int) ($fourthWatch->get() !== null), '|';
