<?php
namespace W343Other;
class Other343 {}
namespace W343B;
use W343Other\Other343 as Alias343;
class Box343 {
    public Alias343|namespace\SeLf $v {
        &get =>
            $this->v;
    }
}
namespace W343BX;
use stdClass as Box343;
use stdClass as Alias343;
$box341 = new \W343B\Box343();
$seed341 = new \W343B\Box343();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \W343B\Box343();
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
$r341 = new \W343Other\Other343();
echo $r341 instanceof \W343Other\Other343 && $r341 === $s341 && $r341 !== $kept341 ? 'A|' : 'BAD|';
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
