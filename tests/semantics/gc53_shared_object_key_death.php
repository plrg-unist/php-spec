<?php
class GC53Value { public $child = null; }
function makeSharedObjectFailure53() { return new Exception('shared-object-53'); }
class GC53Child {
    public function __destruct() {
        global $left, $scalarKey, $valueWatch, $keyWatch, $leftWatch, $rightWatch, $failure;
        echo 'C|', (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($leftWatch->get() !== null), '|',
             (int) ($rightWatch->get() !== null), '|',
             (int) ($left[$scalarKey] === 0), '|';
        throw $failure;
    }
}
$failure = makeSharedObjectFailure53();
$left = new WeakMap;
$right = new WeakMap;
$key = new stdClass;
$scalarKey = new stdClass;
$leftWatch = WeakReference::create($left);
$rightWatch = WeakReference::create($right);
$value = new GC53Value;
$value->child = new GC53Child;
$valueWatch = WeakReference::create($value);
echo 'B|';
$left[$key] = $value;
$right[$key] = $value;
$keyWatch = WeakReference::create($key);
unset($value);
$left[$scalarKey] = 0;
echo 'S|', (int) ($left[$key] === $right[$key]), '|',
     (int) ($valueWatch->get() !== null), '|';
$after = 0;
try {
    unset($key);
    $after = 1;
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo 'T|', (int) ($e === $failure), '|', $trace[0]['function'], '|',
         $after, '|', (int) ($keyWatch->get() === null), '|',
         (int) ($valueWatch->get() === null), '|',
         (int) ($leftWatch->get() !== null), '|',
         (int) ($rightWatch->get() !== null), '|';
}
unset($left, $right);
echo 'A|', (int) ($leftWatch->get() === null), '|',
     (int) ($rightWatch->get() === null), '|';
