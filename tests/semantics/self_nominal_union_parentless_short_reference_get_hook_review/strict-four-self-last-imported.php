<?php
declare(strict_types=1);
namespace D344P;
class First344 {}
class Second344 {}
class Third344 {}
namespace D344B;
use D344P\First344 as One344;
use D344P as Tree344;
class Box344 {
    public tReE344\Second344|\D344P\Third344|oNe344|SeLf $v {
        &get =>
            $this->v;
    }
}
namespace D344BX;
use stdClass as Box344;
use stdClass as One344;
use stdClass as Tree344;
$box341 = new \D344B\Box344();
$seed341 = new \D344B\Box344();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \D344B\Box344();
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
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'N|' : 'BAD|';
}
unset($error341);
$s341 = new \D344P\Second344();
echo $r341 instanceof \D344P\Second344 && $r341 === $s341 && $r341 !== $kept341 ? 'A|' : 'BAD|';
$otherread344 = $box341->v;
echo $otherread344 instanceof \D344P\Second344 && $otherread344 === $r341 && $otherread344 === $s341 ? 'R0|' : 'BAD|';
unset($otherread344);
$r341 = new \D344P\Third344();
echo $r341 instanceof \D344P\Third344 && $r341 === $s341 && $r341 !== $kept341 ? 'B|' : 'BAD|';
$otherread344 = $box341->v;
echo $otherread344 instanceof \D344P\Third344 && $otherread344 === $r341 && $otherread344 === $s341 ? 'R1|' : 'BAD|';
unset($otherread344);
$s341 = new \D344P\First344();
echo $r341 instanceof \D344P\First344 && $r341 === $s341 && $r341 !== $kept341 ? 'C|' : 'BAD|';
$otherread344 = $box341->v;
echo $otherread344 instanceof \D344P\First344 && $otherread344 === $r341 && $otherread344 === $s341 ? 'R2|' : 'BAD|';
unset($otherread344);
$r341 = $kept341;
$read341 = $box341->v;
echo $read341 === $r341 && $kept341 === $s341 && $copy341 !== $r341 ? 'P|' : 'BAD|';
unset($read341);
unset($box341);
$s341 = [];
echo $r341 === [] && $copy341 !== $kept341 ? 'F|' : 'BAD|';
$r341 = false;
$copy341 = 0;
$kept341 = 0;
unset($r341, $s341, $copy341, $kept341);
echo 'Z|';
