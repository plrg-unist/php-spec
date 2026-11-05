<?php
class GC52Value { public $one = null; public $two = null; }
class GC52X {
    public function __destruct() {
        global $map, $scalarKey, $keyWatch, $aWatch, $bWatch;
        echo 'X|', (int) ($keyWatch->get() === null), '|',
             (int) ($aWatch->get() === null), '|',
             (int) ($bWatch->get() === null), '|',
             (int) ($map[$scalarKey] === 0), '|';
    }
}
class GC52Y {
    public function __destruct() {
        global $map, $scalarKey, $keyWatch, $aWatch, $bWatch;
        echo 'Y|', (int) ($keyWatch->get() === null), '|',
             (int) ($aWatch->get() !== null), '|',
             (int) ($bWatch->get() === null), '|',
             (int) ($map[$scalarKey] === 0), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$scalarKey = new stdClass;
$keyWatch = WeakReference::create($key);
$a = new GC52Value;
$x = new GC52X;
$a->one = $x;
$a->two = $x;
unset($x);
$b = new GC52Value;
$b->one = new GC52Y;
$aWatch = WeakReference::create($a);
$bWatch = WeakReference::create($b);
$array = [$a, $b, $a, 0];
unset($a, $b);
echo 'B|';
$map[$key] = $array;
$map[$scalarKey] = 0;
unset($array);
$held = $map[$key];
echo 'R|', (int) isset($map[$key]), '|', (int) !empty($map[$key]), '|',
     (int) ($held[0] === $held[2]), '|';
unset($key);
echo 'H|', (int) ($keyWatch->get() === null), '|',
     (int) ($aWatch->get() !== null), '|',
     (int) ($bWatch->get() !== null), '|',
     (int) ($held[0] === $held[2]), '|';
unset($held);
echo 'V|', (int) ($aWatch->get() === null), '|',
     (int) ($bWatch->get() === null), '|',
     (int) isset($map[$scalarKey]), '|';
unset($map);
echo 'A|';
