<?php
declare(strict_types=1);
namespace D347B;
use \D347B\A347 as Alpha;
interface A347 {}
interface B347 {}
class Payload347 implements A347, B347 {}
class OnlyA347 implements A347 {}
class OnlyB347 implements B347 {}
class Box347 {
    public array|null|(\D347B\B347&aLpHa)|namespace\SeLf $v {
        &get =>
            $this->v;
    }
}
namespace D347BX;
use stdClass as Box347;
use stdClass as Payload347;
use stdClass as Alpha;
use stdClass as B347;
$box341 = new \D347B\Box347();
$seed341 = new \D347B\Box347();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \D347B\Box347();
$kept341 = $r341;
echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'O|' : 'BAD|';
try { $r341 = new \stdClass(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'W|' : 'BAD|';
}
unset($error341);
try { $r341 = new \D347B\OnlyA347(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'M0|' : 'BAD|';
}
unset($error341);
try { $r341 = new \D347B\OnlyB347(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'M1|' : 'BAD|';
}
unset($error341);
try { $r341 = 11; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'J|' : 'BAD|';
}
unset($error341);
try { $r341 = 'strict347'; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'T|' : 'BAD|';
}
unset($error341);
try { $r341 = true; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'S|' : 'BAD|';
}
unset($error341);
$r341 = new \D347B\Payload347();
echo $r341 === $s341 && $r341 instanceof \D347B\Payload347 ? 'D|' : 'BAD|';
$read347 = $box341->v;
echo $read347 === $r341 && $read347 === $s341 ? 'R0|' : 'BAD|';
unset($read347);
$s341 = null;
echo $r341 === null && $s341 === null ? 'Q|' : 'BAD|';
$read347 = $box341->v;
echo $read347 === $r341 && $read347 === $s341 ? 'R1|' : 'BAD|';
unset($read347);
$r341 = [251];
echo $r341[0] === 251 && $s341[0] === 251 ? 'A|' : 'BAD|';
$arraycopy347 = $r341;
$arraycopy347[0] = 263;
echo $r341[0] === 251 && $arraycopy347[0] === 263 ? 'K|' : 'BAD|';
$read347 = $box341->v;
echo $read347 === $r341 && $read347 === $s341 ? 'R2|' : 'BAD|';
unset($read347);
$r341 = $kept341;
$read341 = $box341->v;
echo $read341 === $r341 && $kept341 === $s341 && $copy341 !== $r341 ? 'P|' : 'BAD|';
unset($read341);
unset($arraycopy347);
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
