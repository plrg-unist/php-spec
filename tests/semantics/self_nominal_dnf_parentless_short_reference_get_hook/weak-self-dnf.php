<?php
namespace W347A;
interface A347 {}
interface B347 {}
class Payload347 implements A347, B347 {}
class OnlyA347 implements A347 {}
class Box347 {
    public (A347&namespace\B347)|self $v {
        &get =>
            $this->v;
    }
}
namespace W347AX;
use stdClass as Box347;
use stdClass as A347;
use stdClass as B347;
$box341 = new \W347A\Box347();
$seed341 = new \W347A\Box347();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \W347A\Box347();
$kept341 = $r341;
echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'O|' : 'BAD|';
try { $r341 = new \stdClass(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'W|' : 'BAD|';
}
unset($error341);
try { $r341 = new \W347A\OnlyA347(); } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'J|' : 'BAD|';
}
unset($error341);
try { $r341 = 37; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'N|' : 'BAD|';
}
unset($error341);
$r341 = new \W347A\Payload347();
echo $r341 === $s341 && $r341 instanceof \W347A\Payload347 ? 'D|' : 'BAD|';
$read347 = $box341->v;
echo $read347 === $r341 && $read347 === $s341 ? 'R|' : 'BAD|';
unset($read347);
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
