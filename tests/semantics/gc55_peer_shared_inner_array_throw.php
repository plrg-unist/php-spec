<?php
class NestedArrayValue55 { public $child; }
class NestedArrayX55 {
    public function __destruct() {
        global $aWatch55, $bWatch55, $mapWatch55, $keyWatch55;
        echo 'X|', (int) ($aWatch55->get() === NULL), '|',
            (int) ($bWatch55->get() === NULL), '|',
            (int) ($mapWatch55->get() !== NULL), '|',
            (int) ($keyWatch55->get() !== NULL), '|';
    }
}
class NestedArrayY55 {
    public function __destruct() {
        global $aWatch55, $bWatch55, $mapWatch55, $keyWatch55, $failure55;
        echo 'Y|', (int) ($aWatch55->get() !== NULL), '|',
            (int) ($bWatch55->get() === NULL), '|',
            (int) ($mapWatch55->get() !== NULL), '|',
            (int) ($keyWatch55->get() !== NULL), '|';
        throw $failure55;
    }
}
function makeNestedArrayFailure55() { return new Exception('nested array'); }
$failure55 = makeNestedArrayFailure55();
$a55 = new NestedArrayValue55();
$a55->child = new NestedArrayX55();
$b55 = new NestedArrayValue55();
$b55->child = new NestedArrayY55();
$aWatch55 = WeakReference::create($a55);
$bWatch55 = WeakReference::create($b55);
$inner55 = [$a55, $b55, $a55];
unset($a55, $b55);
$map = new WeakMap();
$key = new stdClass();
$mapWatch55 = WeakReference::create($map);
$keyWatch55 = WeakReference::create($key);
echo 'B|';
$map[$key] = [$inner55, $inner55, 0];
unset($inner55);
echo 'S|', (int) ($aWatch55->get() !== NULL), '|',
    (int) ($bWatch55->get() !== NULL), '|';
$after55 = 0;
try {
    unset($map);
    $after55 = 1;
} catch (Throwable $caught55) {
    echo 'T|', (int) ($caught55 === $failure55), '|',
        $caught55->getTrace()[0]['function'], '|', $after55, '|',
        (int) ($mapWatch55->get() === NULL), '|',
        (int) ($aWatch55->get() === NULL), '|',
        (int) ($bWatch55->get() === NULL), '|',
        (int) ($keyWatch55->get() !== NULL), '|';
}
unset($key);
echo 'A|', (int) ($keyWatch55->get() === NULL), '|';
