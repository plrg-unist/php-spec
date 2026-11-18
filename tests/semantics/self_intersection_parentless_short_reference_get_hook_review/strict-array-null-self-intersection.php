<?php
declare(strict_types=1);
namespace D348B;
interface I348 {}
class OnlyI348 implements I348 {}
class Box348 implements I348 {
    public array|null|(namespace\I348&self) $v {
        &get =>
            $this->v;
    }
}
namespace D348BX;
use stdClass as Box348;
use stdClass as I348;
$box341 = new \D348B\Box348();
$seed341 = new \D348B\Box348();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \D348B\Box348();
$kept341 = $r341;
echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'O|' : 'BAD|';
try { $r341 = new \D348B\OnlyI348(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'M|' : 'BAD|';
}
unset($error341);
try { $r341 = '127'; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'S|' : 'BAD|';
}
unset($error341);
$s341 = null;
echo $r341 === null && $s341 === null ? 'Q|' : 'BAD|';
$read348 = $box341->v;
echo $read348 === $r341 && $read348 === $s341 ? 'R|' : 'BAD|';
unset($read348);
$r341 = [251];
echo $r341[0] === 251 && $s341[0] === 251 ? 'A|' : 'BAD|';
$arraycopy348 = $r341;
$arraycopy348[0] = 263;
echo $r341[0] === 251 && $s341[0] === 251 && $arraycopy348[0] === 263 ? 'K|' : 'BAD|';
unset($arraycopy348);
$read348 = $box341->v;
echo $read348 === $r341 && $read348 === $s341 ? 'R|' : 'BAD|';
unset($read348);
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
