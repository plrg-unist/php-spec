<?php
class GC55Value { public $child = null; }
class GC55X {
    public function __destruct() {
        global $map, $scalarKey, $keyWatch, $aWatch, $bWatch;
        echo 'X|', (int) ($keyWatch->get() === null), '|',
             (int) ($aWatch->get() === null), '|',
             (int) ($bWatch->get() === null), '|',
             (int) ($map[$scalarKey] === 0), '|';
    }
}
class GC55Y {
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
$a = new GC55Value;
$a->child = new GC55X;
$b = new GC55Value;
$b->child = new GC55Y;
$aWatch = WeakReference::create($a);
$bWatch = WeakReference::create($b);
$inner = [$a, $b, $a];
$middle = [$inner];
$outer = [$middle, $inner, 0];
unset($a, $b, $inner, $middle);
echo 'B|';
$map[$key] = $outer;
$map[$scalarKey] = 0;
unset($outer);
$held = $map[$key];
$copy = $held;
unset($copy[0]);
echo 'R|', (int) ($held[0][0][0] === $held[1][2]), '|',
     (int) ($copy[1][0] === $held[1][2]), '|',
     (int) ($copy[1][1] === $held[0][0][1]), '|';
unset($key);
echo 'H|', (int) ($keyWatch->get() === null), '|',
     (int) ($aWatch->get() !== null), '|',
     (int) ($bWatch->get() !== null), '|',
     (int) ($held[0][0][0] === $copy[1][2]), '|';
unset($held);
echo 'D|', (int) ($aWatch->get() !== null), '|',
     (int) ($bWatch->get() !== null), '|';
unset($copy);
echo 'V|', (int) ($aWatch->get() === null), '|',
     (int) ($bWatch->get() === null), '|',
     (int) ($map[$scalarKey] === 0), '|';
unset($map);
echo 'A|';
