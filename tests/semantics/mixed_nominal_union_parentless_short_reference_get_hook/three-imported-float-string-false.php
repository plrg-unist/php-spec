<?php
namespace P335;
class A { public $tag = 61; }
class B { public $tag = 71; }
class C { public $tag = 81; }
namespace W335C;
use P335 as Tree;
use P335\A as Alpha;
class Box335 {
    public float|tReE\C|false|aLpHa|string|\P335\B $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W335CX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
use stdClass as Tree;
use stdClass as Alpha;
$box335 = new \W335C\Box335();
$seed335 = new \P335\A();
$box335->v = $seed335;
unset($seed335);
$r335 =& $box335->v;
$s335 =& $r335;
echo $r335 === $s335 && $r335->tag === 61 ? 'I|' : 'BAD|';
$copy335 = $box335->v;
$copy335->tag = 67;
echo $copy335 === $r335 && $r335 === $s335 && $r335->tag === 67 ? 'C|' : 'BAD|';
$s335 = new \P335\B();
echo $r335 === $s335 && $r335->tag === 71 && $copy335->tag === 67 ? 'O1|' : 'BAD|';
$r335 = new \P335\C();
echo $r335 === $s335 && $r335->tag === 81 && $copy335->tag === 67 ? 'O2|' : 'BAD|';
$kept335 = $r335;
try { $r335 = new \stdClass(); } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 81 && $copy335->tag === 67 ? 'W|' : 'BAD|';
}
unset($error335);
try { $r335 = []; } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 81 && $copy335->tag === 67 ? 'J|' : 'BAD|';
}
unset($error335);
$r335 = 3;
echo $r335 === 3.0 && $s335 === 3.0 ? 'V|' : 'BAD|';
$s335 = 'quiet';
echo $r335 === 'quiet' && $s335 === 'quiet' ? 'S|' : 'BAD|';
$r335 = false;
echo $r335 === false && $s335 === false ? 'L|' : 'BAD|';
$s335 = true;
echo $r335 === 1.0 && $s335 === 1.0 ? 'T|' : 'BAD|';
$r335 = $kept335;
$read335 = $box335->v;
echo $read335 === $r335 && $kept335 === $s335 && $copy335->tag === 67 ? 'P|' : 'BAD|';
unset($read335);
unset($box335);
$s335 = [];
echo $r335 === [] && $copy335->tag === 67 && $kept335->tag === 81 ? 'F|' : 'BAD|';
$r335 = false;
$copy335 = 0;
$kept335 = 0;
unset($r335, $s335, $copy335, $kept335);
echo 'Z|';
