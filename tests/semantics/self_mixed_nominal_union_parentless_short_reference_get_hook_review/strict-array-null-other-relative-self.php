<?php
declare(strict_types=1);
namespace D346B;
use \D346B\Other346 as Alt346;
class Other346 {}
class Box346 {
    public array|null|namespace\Other346|namespace\SeLf $v {
        &get =>
            $this->v;
    }
}
namespace D346BX;
use stdClass as Box346;
use stdClass as Other346;
use stdClass as Alt346;
$box341 = new \D346B\Box346();
$seed341 = new \D346B\Box346();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \D346B\Box346();
$kept341 = $r341;
echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'O|' : 'BAD|';
try { $r341 = new \stdClass(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'W|' : 'BAD|';
}
unset($error341);
try { $r341 = 11; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'J|' : 'BAD|';
}
unset($error341);
try { $r341 = 'strict346'; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'T|' : 'BAD|';
}
unset($error341);
$r341 = new \D346B\Other346();
echo $r341 === $s341 && $r341 instanceof \D346B\Other346 ? 'D|' : 'BAD|';
$read346 = $box341->v;
echo $read346 === $r341 && $read346 === $s341 ? 'R0|' : 'BAD|';
unset($read346);
$s341 = null;
echo $r341 === null && $s341 === null ? 'Q|' : 'BAD|';
$read346 = $box341->v;
echo $read346 === $r341 && $read346 === $s341 ? 'R1|' : 'BAD|';
unset($read346);
$r341 = [211];
echo $r341[0] === 211 && $s341[0] === 211 ? 'A|' : 'BAD|';
$arraycopy346 = $r341;
$arraycopy346[0] = 223;
echo $r341[0] === 211 && $arraycopy346[0] === 223 ? 'K|' : 'BAD|';
$read346 = $box341->v;
echo $read346 === $r341 && $read346 === $s341 ? 'R2|' : 'BAD|';
unset($read346);
$r341 = $kept341;
$read341 = $box341->v;
echo $read341 === $r341 && $kept341 === $s341 && $copy341 !== $r341 ? 'P|' : 'BAD|';
unset($read341);
unset($arraycopy346);
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
