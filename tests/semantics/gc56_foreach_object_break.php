<?php
class GC56Value { public $child = null; }
class GC56Child {
    public function __destruct() {
        global $mapWatch56, $keyWatch56, $valueWatch56;
        echo 'C|', (int) ($mapWatch56->get() === null), '|',
             (int) ($keyWatch56->get() === null), '|',
             (int) ($valueWatch56->get() === null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC56Value;
$value->child = new GC56Child;
$mapWatch56 = WeakReference::create($map);
$keyWatch56 = WeakReference::create($key);
$valueWatch56 = WeakReference::create($value);
$map[$key] = $value;
unset($value);
echo 'B|';
foreach ($map as $loopKey => $loopValue) {
    unset($map);
    echo 'L|', (int) ($mapWatch56->get() !== null), '|',
         (int) ($loopKey === $key), '|',
         (int) ($valueWatch56->get() === $loopValue), '|';
    break;
}
echo 'D|', (int) ($mapWatch56->get() === null), '|',
     (int) ($valueWatch56->get() === $loopValue), '|';
unset($key);
echo 'K|', (int) ($keyWatch56->get() === $loopKey), '|';
unset($loopKey);
echo 'V|', (int) ($keyWatch56->get() === null), '|',
     (int) ($valueWatch56->get() === $loopValue), '|';
unset($loopValue);
echo 'A|', (int) ($valueWatch56->get() === null), '|';
