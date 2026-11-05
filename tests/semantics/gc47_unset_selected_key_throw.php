<?php
class GC47Value { public $a = null; public $b = null; public $c = null; }
class GC47Leaf {}
function makeFailure47() { return new Exception('unset-47'); }
function selectedKey47($candidate) {
    global $key, $keyWatch;
    $key = null;
    echo 'K|', (int) ($keyWatch->get() === $candidate), '|';
    return $candidate;
}
class GC47X {
    public function __destruct() {
        global $map, $mapWatch, $valueWatch, $keyWatch, $yWatch, $leftWatch, $rightWatch;
        $observedKey = $keyWatch->get();
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($observedKey !== null), '|',
             (int) !isset($map[$observedKey]), '|',
             (int) empty($map[$observedKey]), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($leftWatch->get() !== null), '|',
             (int) ($rightWatch->get() !== null), '|';
    }
}
class GC47Y {
    public function __destruct() {
        global $map, $mapWatch, $valueWatch, $keyWatch, $xWatch, $leftWatch, $rightWatch, $failure;
        $observedKey = $keyWatch->get();
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($observedKey !== null), '|',
             (int) !isset($map[$observedKey]), '|',
             (int) empty($map[$observedKey]), '|',
             (int) ($xWatch->get() !== null), '|',
             (int) ($leftWatch->get() !== null), '|',
             (int) ($rightWatch->get() !== null), '|';
        throw $failure;
    }
}
$failure = makeFailure47();
$map = new WeakMap;
$key = new stdClass;
$leftKey = new stdClass;
$rightKey = new stdClass;
$value = new GC47Value;
$x = new GC47X;
$y = new GC47Y;
$left = new GC47Leaf;
$right = new GC47Leaf;
$value->c = $x;
$value->b = $y;
$value->a = $x;
$map[$key] = $value;
$map[$leftKey] = $left;
$map[$rightKey] = $right;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$keyWatch = WeakReference::create($key);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$leftWatch = WeakReference::create($left);
$rightWatch = WeakReference::create($right);
unset($value, $x, $y, $left, $right);
$continued = 0;
echo 'B|';
try {
    unset($map[selectedKey47($key)]);
    $continued = 1;
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo 'T|', (int) ($e === $failure), '|', $continued, '|',
         $trace[0]['function'], '|',
         (int) ($keyWatch->get() === null), '|',
         (int) ($valueWatch->get() === null), '|',
         (int) ($xWatch->get() === null), '|',
         (int) ($yWatch->get() === null), '|';
}
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($leftWatch->get() === null), '|',
     (int) ($rightWatch->get() === null), '|';
