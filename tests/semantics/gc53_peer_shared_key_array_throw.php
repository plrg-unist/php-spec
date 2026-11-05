<?php
class SharedArrayValue53 { public $child; }
class SharedArrayX53 {
    public function __destruct() {
        global $keyWatch53, $aWatch53, $bWatch53, $map2Watch53;
        echo 'X|', (int) ($keyWatch53->get() !== NULL), '|',
            (int) ($aWatch53->get() === NULL), '|',
            (int) ($bWatch53->get() === NULL), '|',
            (int) ($map2Watch53->get() !== NULL), '|';
    }
}
class SharedArrayY53 {
    public function __destruct() {
        global $map1Watch53, $map2Watch53, $keyWatch53, $aWatch53, $bWatch53;
        global $map2, $other53, $failure53;
        echo 'Y|', (int) ($map1Watch53->get() === NULL), '|',
            (int) ($map2Watch53->get() !== NULL), '|',
            (int) ($keyWatch53->get() !== NULL), '|',
            (int) ($aWatch53->get() !== NULL), '|',
            (int) ($bWatch53->get() === NULL), '|',
            (int) ($map2[$other53] === 7), '|';
        throw $failure53;
    }
}
function makeSharedFailure53() { return new Exception('shared array'); }
$failure53 = makeSharedFailure53();
$a53 = new SharedArrayValue53();
$a53->child = new SharedArrayX53();
$b53 = new SharedArrayValue53();
$b53->child = new SharedArrayY53();
$aWatch53 = WeakReference::create($a53);
$bWatch53 = WeakReference::create($b53);
$payload53 = [$a53, $b53, $a53];
unset($a53, $b53);
$key53 = new stdClass();
$other53 = new stdClass();
$map1 = new WeakMap();
$map2 = new WeakMap();
$map1Watch53 = WeakReference::create($map1);
$map2Watch53 = WeakReference::create($map2);
echo 'B|';
$map1[$key53] = $payload53;
$map2[$key53] = $payload53;
$map2[$other53] = 7;
$keyWatch53 = WeakReference::create($key53);
unset($payload53);
unset($map1);
echo 'S|', (int) ($map1Watch53->get() === NULL), '|',
    (int) ($aWatch53->get() !== NULL), '|',
    (int) ($bWatch53->get() !== NULL), '|',
    (int) ($map2[$other53] === 7), '|';
$after53 = 0;
try {
    unset($key53);
    $after53 = 1;
} catch (Throwable $caught53) {
    echo 'T|', (int) ($caught53 === $failure53), '|',
        $caught53->getTrace()[0]['function'], '|', $after53, '|',
        (int) ($keyWatch53->get() === NULL), '|',
        (int) ($aWatch53->get() === NULL), '|',
        (int) ($bWatch53->get() === NULL), '|',
        (int) ($map2[$other53] === 7), '|';
}
unset($map2);
echo 'A|', (int) ($map2Watch53->get() === NULL), '|';
