<?php
declare(strict_types=1);
namespace D341B;
use stdClass as Irrelevant341;
class Box341 {
    public int|self $v {
        &get =>
            $this->v;
    }
}
namespace D341BX;
use stdClass as Box341;
$box341 = new \D341B\Box341();
$seed341 = new \D341B\Box341();
$box341->v = $seed341;
unset($seed341);
$r341 =& $box341->v;
$s341 =& $r341;
echo $r341 === $s341 ? 'I|' : 'BAD|';
$copy341 = $box341->v;
echo $copy341 === $r341 ? 'C|' : 'BAD|';
$s341 = new \D341B\Box341();
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
try { $r341 = '127'; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'S|' : 'BAD|';
}
unset($error341);
try { $s341 = true; } catch (\TypeError $error341) {
    echo $r341 === $s341 && $r341 === $kept341 && $copy341 !== $r341 ? 'T|' : 'BAD|';
}
unset($error341);
$r341 = 127;
echo $r341 === 127 && $s341 === 127 ? 'N|' : 'BAD|';
$s341 = 1;
echo $r341 === 1 && $s341 === 1 ? 'B|' : 'BAD|';
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
