<?php
class GC56ArrayValue { public $child = null; }
class GC56ArrayChild {
    public function __destruct() {
        global $mapWatch56, $keyWatch56, $valueWatch56;
        echo 'C|', (int) ($mapWatch56->get() === null), '|',
             (int) ($keyWatch56->get() === null), '|',
             (int) ($valueWatch56->get() === null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC56ArrayValue;
$value->child = new GC56ArrayChild;
$mapWatch56 = WeakReference::create($map);
$keyWatch56 = WeakReference::create($key);
$valueWatch56 = WeakReference::create($value);
$inner = [$value, 0];
$outer = [$inner, $inner];
$map[$key] = $outer;
unset($value, $inner, $outer);
echo 'B|';
foreach ($map as $loopKey => $loopValue) {
    unset($map);
    echo 'L|', (int) ($mapWatch56->get() !== null), '|',
         (int) ($loopKey === $key), '|',
         (int) ($loopValue[0][0] === $loopValue[1][0]), '|';
    break;
}
echo 'D|', (int) ($mapWatch56->get() === null), '|',
     (int) ($valueWatch56->get() === $loopValue[1][0]), '|';
unset($key, $loopKey);
echo 'V|', (int) ($keyWatch56->get() === null), '|',
     (int) ($valueWatch56->get() === $loopValue[0][0]), '|';
unset($loopValue);
echo 'A|', (int) ($valueWatch56->get() === null), '|';
