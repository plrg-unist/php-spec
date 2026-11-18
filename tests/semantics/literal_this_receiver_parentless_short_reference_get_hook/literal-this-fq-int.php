<?php
namespace W336A;
class A { public $tag = 61; }
class B { public $tag = 71; }
class Box336 {
    public \W336A\A|int|\W336A\B $v {
        &get =>
            ${'this'}->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W336AX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
use stdClass as Tree;
use stdClass as Alpha;
$box335 = new \W336A\Box336();
$seed335 = new \W336A\A();
$box335->v = $seed335;
unset($seed335);
$r335 =& $box335->v;
$s335 =& $r335;
echo $r335 === $s335 && $r335->tag === 61 ? 'I|' : 'BAD|';
$copy335 = $box335->v;
$copy335->tag = 67;
echo $copy335 === $r335 && $r335 === $s335 && $r335->tag === 67 ? 'C|' : 'BAD|';
$s335 = new \W336A\B();
echo $r335 === $s335 && $r335->tag === 71 && $copy335->tag === 67 ? 'O1|' : 'BAD|';
$kept335 = $r335;
try { $r335 = new \stdClass(); } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 71 && $copy335->tag === 67 ? 'W|' : 'BAD|';
}
unset($error335);
try { $r335 = []; } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 71 && $copy335->tag === 67 ? 'J|' : 'BAD|';
}
unset($error335);
$r335 = '127';
echo $r335 === 127 && $s335 === 127 ? 'N|' : 'BAD|';
$s335 = true;
echo $r335 === 1 && $s335 === 1 ? 'B|' : 'BAD|';
$r335 = $kept335;
$read335 = $box335->v;
echo $read335 === $r335 && $kept335 === $s335 && $copy335->tag === 67 ? 'P|' : 'BAD|';
unset($read335);
unset($box335);
$s335 = [];
echo $r335 === [] && $copy335->tag === 67 && $kept335->tag === 71 ? 'F|' : 'BAD|';
$r335 = false;
$copy335 = 0;
$kept335 = 0;
unset($r335, $s335, $copy335, $kept335);
echo 'Z|';
