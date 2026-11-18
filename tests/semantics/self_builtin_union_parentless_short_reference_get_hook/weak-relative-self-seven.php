<?php
namespace W345B;
class Box345 {
    public string|namespace\SeLf|array|float|int|null|false $v {
        &get =>
            $this->v;
    }
}
namespace W345BX;
use stdClass as Box345;
$box341 = new \W345B\Box345();
$seed341 = new \W345B\Box345();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \W345B\Box345();
$kept341 = $r341;
echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'O|' : 'BAD|';
try { $r341 = new \stdClass(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'W|' : 'BAD|';
}
unset($error341);
$r341 = false;
echo $r341 === false && $s341 === false ? 'L|' : 'BAD|';
$read345 = $box341->v;
echo $read345 === $r341 && $read345 === $s341 ? 'R|' : 'BAD|';
unset($read345);
$s341 = true;
echo $r341 === 1 && $s341 === 1 ? 'B|' : 'BAD|';
$read345 = $box341->v;
echo $read345 === $r341 && $read345 === $s341 ? 'R|' : 'BAD|';
unset($read345);
$r341 = '37.0';
echo $r341 === '37.0' && $s341 === '37.0' ? 'T|' : 'BAD|';
$read345 = $box341->v;
echo $read345 === $r341 && $read345 === $s341 ? 'R|' : 'BAD|';
unset($read345);
$s341 = 37.0;
echo $r341 === 37.0 && $s341 === 37.0 ? 'V|' : 'BAD|';
$read345 = $box341->v;
echo $read345 === $r341 && $read345 === $s341 ? 'R|' : 'BAD|';
unset($read345);
$r341 = 37;
echo $r341 === 37 && $s341 === 37 ? 'E|' : 'BAD|';
$read345 = $box341->v;
echo $read345 === $r341 && $read345 === $s341 ? 'R|' : 'BAD|';
unset($read345);
$s341 = [193];
echo $r341 === [193] && $s341 === [193] ? 'A|' : 'BAD|';
$arraycopy345 = $r341;
$arraycopy345[0] = 197;
echo $r341[0] === 193 && $arraycopy345[0] === 197 ? 'K|' : 'BAD|';
$read345 = $box341->v;
echo $read345 === $r341 && $read345 === $s341 ? 'R|' : 'BAD|';
unset($read345);
$r341 = null;
unset($arraycopy345);
echo $r341 === null && $s341 === null ? 'Q|' : 'BAD|';
$read345 = $box341->v;
echo $read345 === $r341 && $read345 === $s341 ? 'R|' : 'BAD|';
unset($read345);
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
