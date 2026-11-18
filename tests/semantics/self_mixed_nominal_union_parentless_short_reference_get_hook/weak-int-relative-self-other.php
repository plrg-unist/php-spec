<?php
namespace W346B;
class Other346 {}
class Box346 {
    public int|namespace\SeLf|\W346B\Other346 $v {
        &get =>
            $this->v;
    }
}
namespace W346BX;
use stdClass as Box346;
use stdClass as Other346;
$box341 = new \W346B\Box346();
$seed341 = new \W346B\Box346();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \W346B\Box346();
$kept341 = $r341;
echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'O|' : 'BAD|';
try { $r341 = new \stdClass(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'W|' : 'BAD|';
}
unset($error341);
try { $r341 = []; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'J|' : 'BAD|';
}
unset($error341);
try { $r341 = null; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'Q|' : 'BAD|';
}
unset($error341);
$r341 = new \W346B\Other346();
echo $r341 === $s341 && $r341 instanceof \W346B\Other346 ? 'D|' : 'BAD|';
$read346 = $box341->v;
echo $read346 === $r341 && $read346 === $s341 ? 'R|' : 'BAD|';
unset($read346);
$s341 = '127';
echo $r341 === 127 && $s341 === 127 ? 'N|' : 'BAD|';
$read346 = $box341->v;
echo $read346 === $r341 && $read346 === $s341 ? 'R|' : 'BAD|';
unset($read346);
$r341 = true;
echo $r341 === 1 && $s341 === 1 ? 'B|' : 'BAD|';
$read346 = $box341->v;
echo $read346 === $r341 && $read346 === $s341 ? 'R|' : 'BAD|';
unset($read346);
$r341 = $kept341;
$read341 = $box341->v;
echo $read341 === $r341 && $kept341 === $s341 && $copy341 !== $r341 ? 'P|' : 'BAD|';
unset($read341);
unset($box341);
$s341 = [];
echo $r341 === [] && $copy341 !== $kept341 ? 'F|' : 'BAD|';
$r341 = new \stdClass();
echo $r341 instanceof \stdClass && $r341 === $s341 ? 'D|' : 'BAD|';
$r341 = false;
$copy341 = 0;
$kept341 = 0;
unset($r341, $s341, $copy341, $kept341);
echo 'Z|';
