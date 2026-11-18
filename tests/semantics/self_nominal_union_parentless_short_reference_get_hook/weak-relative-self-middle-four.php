<?php
namespace W344Payload;
class First344 {}
class Second344 {}
class Third344 {}
namespace W344B;
use W344Payload\First344 as AliasFirst344;
use W344Payload\Second344 as AliasSecond344;
class Box344 {
    public AliasFirst344|namespace\SeLf|AliasSecond344|\W344Payload\Third344 $v {
        &get =>
            $this->v;
    }
}
namespace W344BX;
use stdClass as Box344;
use stdClass as AliasFirst344;
use stdClass as AliasSecond344;
$box341 = new \W344B\Box344();
$seed341 = new \W344B\Box344();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \W344B\Box344();
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
    echo $r341 === $s341 && $r341 === $kept341 ? 'N|' : 'BAD|';
}
unset($error341);
$r341 = new \W344Payload\First344();
echo $r341 instanceof \W344Payload\First344 && $r341 === $s341 && $r341 !== $kept341 ? 'A|' : 'BAD|';
$read344 = $box341->v;
echo $read344 instanceof \W344Payload\First344 && $read344 === $r341 && $read344 === $s341 ? 'R|' : 'BAD|';
unset($read344);
$s341 = new \W344Payload\Second344();
echo $r341 instanceof \W344Payload\Second344 && $r341 === $s341 && $r341 !== $kept341 ? 'B|' : 'BAD|';
$read344 = $box341->v;
echo $read344 instanceof \W344Payload\Second344 && $read344 === $r341 && $read344 === $s341 ? 'R|' : 'BAD|';
unset($read344);
$r341 = new \W344Payload\Third344();
echo $r341 instanceof \W344Payload\Third344 && $r341 === $s341 && $r341 !== $kept341 ? 'C|' : 'BAD|';
$read344 = $box341->v;
echo $read344 instanceof \W344Payload\Third344 && $read344 === $r341 && $read344 === $s341 ? 'R|' : 'BAD|';
unset($read344);
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
