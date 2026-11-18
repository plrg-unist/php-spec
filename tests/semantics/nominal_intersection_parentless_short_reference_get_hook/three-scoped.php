<?php
namespace P338;
interface A {}
namespace W338B;
interface B {}
interface C {}
namespace P338;
class All338 implements \P338\A,\W338B\C,\W338B\B { public $tag = 61; }
class Missing0338 implements \W338B\C,\W338B\B { public $tag = 81; }
class Missing1338 implements \P338\A,\W338B\B { public $tag = 81; }
class Missing2338 implements \P338\A,\W338B\C { public $tag = 81; }
namespace W338B;
use P338\A as Alpha;
class Box338 {
    public aLpHa&namespace\C&B $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W338BX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
use stdClass as Alpha;
$box338 = new \W338B\Box338();
$box338->v = new \P338\All338();
$r338 =& $box338->v;
$s338 =& $r338;
echo $r338 === $s338 && $r338->tag === 61 ? 'I|' : 'BAD|';
$copy338 = $box338->v;
$copy338->tag = 67;
echo $copy338 === $r338 && $s338->tag === 67 ? 'C|' : 'BAD|';
$s338 = new \P338\All338();
$s338->tag = 71;
echo $r338 === $s338 && $r338->tag === 71 && $copy338->tag === 67 ? 'O|' : 'BAD|';
$kept338 = $r338;
try { $r338 = new \P338\Missing0338(); } catch (\TypeError $error338) {
    echo $r338 === $s338 && $r338 === $kept338 && $r338->tag === 71 ? 'M0|' : 'BAD|';
}
unset($error338);
try { $r338 = new \P338\Missing1338(); } catch (\TypeError $error338) {
    echo $r338 === $s338 && $r338 === $kept338 && $r338->tag === 71 ? 'M1|' : 'BAD|';
}
unset($error338);
try { $r338 = new \P338\Missing2338(); } catch (\TypeError $error338) {
    echo $r338 === $s338 && $r338 === $kept338 && $r338->tag === 71 ? 'M2|' : 'BAD|';
}
unset($error338);
try { $s338 = 17; } catch (\TypeError $error338) {
    echo $r338 === $s338 && $r338 === $kept338 && $r338->tag === 71 ? 'S|' : 'BAD|';
}
unset($error338);
$r338 = $copy338;
$read338 = $box338->v;
echo $read338 === $copy338 && $r338 === $copy338 && $s338 === $copy338 && $kept338->tag === 71 ? 'P|' : 'BAD|';
unset($read338);
unset($box338);
$s338 = [];
echo $r338 === [] && $copy338->tag === 67 && $kept338->tag === 71 ? 'F|' : 'BAD|';
$r338 = false;
$copy338 = 0;
$kept338 = 0;
unset($r338, $s338, $copy338, $kept338);
echo 'Z|';
