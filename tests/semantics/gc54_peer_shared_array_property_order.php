<?php
class ArrayPropertyValue54 {
    public $first;
    public $middle;
    public $last;
}
class ArrayPropertyX54 {
    public function __destruct() {
        global $valueWatch54, $mapWatch54, $keyWatch54, $yWatch54, $zWatch54;
        echo 'X|', (int) ($valueWatch54->get() === NULL), '|',
            (int) ($mapWatch54->get() !== NULL), '|',
            (int) ($keyWatch54->get() !== NULL), '|',
            (int) ($yWatch54->get() === NULL), '|',
            (int) ($zWatch54->get() === NULL), '|';
    }
}
class ArrayPropertyY54 {
    public function __destruct() {
        global $valueWatch54, $mapWatch54, $keyWatch54, $xWatch54, $zWatch54;
        global $failure54;
        echo 'Y|', (int) ($valueWatch54->get() === NULL), '|',
            (int) ($mapWatch54->get() !== NULL), '|',
            (int) ($keyWatch54->get() !== NULL), '|',
            (int) ($xWatch54->get() !== NULL), '|',
            (int) ($zWatch54->get() !== NULL), '|';
        throw $failure54;
    }
}
class ArrayPropertyZ54 {
    public function __destruct() {
        global $valueWatch54, $mapWatch54, $keyWatch54, $yWatch54, $xWatch54;
        echo 'Z|', (int) ($valueWatch54->get() === NULL), '|',
            (int) ($mapWatch54->get() !== NULL), '|',
            (int) ($keyWatch54->get() !== NULL), '|',
            (int) ($yWatch54->get() === NULL), '|',
            (int) ($xWatch54->get() !== NULL), '|';
    }
}
function makeArrayPropertyFailure54() { return new Exception('property array'); }
$failure54 = makeArrayPropertyFailure54();
$x54 = new ArrayPropertyX54();
$y54 = new ArrayPropertyY54();
$z54 = new ArrayPropertyZ54();
$xWatch54 = WeakReference::create($x54);
$yWatch54 = WeakReference::create($y54);
$zWatch54 = WeakReference::create($z54);
$array54 = [$x54, 0, $z54, $x54];
$value = new ArrayPropertyValue54();
$value->last = $array54;
$value->middle = $y54;
$value->first = $array54;
$valueWatch54 = WeakReference::create($value);
unset($array54, $x54, $y54, $z54);
$map = new WeakMap();
$key = new stdClass();
$mapWatch54 = WeakReference::create($map);
$keyWatch54 = WeakReference::create($key);
echo 'B|';
$map[$key] = $value;
unset($value);
echo 'S|';
$after54 = 0;
try {
    unset($map);
    $after54 = 1;
} catch (Throwable $caught54) {
    echo 'T|', (int) ($caught54 === $failure54), '|',
        $caught54->getTrace()[0]['function'], '|', $after54, '|',
        (int) ($mapWatch54->get() === NULL), '|',
        (int) ($valueWatch54->get() === NULL), '|',
        (int) ($xWatch54->get() === NULL), '|',
        (int) ($yWatch54->get() === NULL), '|',
        (int) ($zWatch54->get() === NULL), '|',
        (int) ($keyWatch54->get() !== NULL), '|';
}
unset($key);
echo 'A|', (int) ($keyWatch54->get() === NULL), '|';
