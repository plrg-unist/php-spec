<?php
declare(strict_types=1);
namespace D345A;
class Box345 {
    public array|SeLf|null $v {
        &get =>
            $this->v;
    }
}
namespace D345AX;
use stdClass as Box345;
$box341 = new \D345A\Box345();
$seed341 = new \D345A\Box345();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \D345A\Box345();
$kept341 = $r341;
echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'O|' : 'BAD|';
try { $r341 = new \stdClass(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'W|' : 'BAD|';
}
unset($error341);
try { $r341 = 7; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'J|' : 'BAD|';
}
unset($error341);
try { $r341 = false; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'S|' : 'BAD|';
}
unset($error341);
try { $r341 = 'strict345'; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'T|' : 'BAD|';
}
unset($error341);
try { $r341 = 1.0; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'V|' : 'BAD|';
}
unset($error341);
$r341 = null;
echo $r341 === null && $s341 === null ? 'N|' : 'BAD|';
$read345 = $box341->v;
echo $read345 === $r341 && $read345 === $s341 ? 'R0|' : 'BAD|';
unset($read345);
$s341 = [193];
echo $r341[0] === 193 && $s341[0] === 193 ? 'A|' : 'BAD|';
$arraycopy345 = $r341;
$arraycopy345[0] = 197;
echo $r341[0] === 193 && $arraycopy345[0] === 197 ? 'K|' : 'BAD|';
$read345 = $box341->v;
echo $read345 === $r341 && $read345 === $s341 ? 'R1|' : 'BAD|';
unset($read345);
$r341 = $kept341;
unset($arraycopy345);
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
