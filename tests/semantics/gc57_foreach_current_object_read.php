<?php
class GC57Value { public $child = null; }
class GC57Child {
    public function __destruct() {
        global $mapWatch57, $keyWatch57, $valueWatch57;
        echo 'C|', (int) ($mapWatch57->get() === null), '|',
             (int) ($keyWatch57->get() === null), '|',
             (int) ($valueWatch57->get() === null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$scalarKey = new stdClass;
$value = new GC57Value;
$value->child = new GC57Child;
$mapWatch57 = WeakReference::create($map);
$keyWatch57 = WeakReference::create($key);
$valueWatch57 = WeakReference::create($value);
$map[$key] = $value;
$map[$scalarKey] = 17;
unset($value);
echo 'B|';
foreach ($map as $loopKey => $loopValue) {
    $held = $map[$loopKey];
    echo 'R|', (int) ($held === $loopValue), '|',
         (int) ($valueWatch57->get() === $held), '|';
    unset($loopValue, $map);
    echo 'L|', (int) ($mapWatch57->get() !== null), '|',
         (int) ($keyWatch57->get() === $loopKey), '|';
    break;
}
echo 'D|', (int) ($mapWatch57->get() === null), '|',
     (int) ($valueWatch57->get() === $held), '|';
unset($key, $scalarKey);
echo 'K|', (int) ($keyWatch57->get() === $loopKey), '|';
unset($loopKey);
echo 'V|', (int) ($keyWatch57->get() === null), '|',
     (int) ($valueWatch57->get() === $held), '|';
unset($held);
echo 'A|', (int) ($valueWatch57->get() === null), '|';
