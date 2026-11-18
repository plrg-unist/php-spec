<?php
declare(strict_types=1);
namespace I336A;
class A { public $tag = 61; }
class B { public $tag = 71; }
class Box336 {
    public bool|\I336A\B|\I336A\A $v {
        &get =>
            ${"\x74his"}->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace I336AX;
use stdClass as A;
use stdClass as B;
$box335 = new \I336A\Box336();
$seed335 = new \I336A\A();
$box335->v = $seed335;
unset($seed335);
$r335 =& $box335->v;
$s335 =& $r335;
echo $r335 === $s335 && $r335->tag === 61 ? 'I|' : 'BAD|';
$copy335 = $box335->v;
$copy335->tag = 67;
echo $copy335 === $r335 && $r335 === $s335 && $r335->tag === 67 ? 'C|' : 'BAD|';
$s335 = new \I336A\B();
echo $r335 === $s335 && $r335->tag === 71 && $copy335->tag === 67 ? 'O1|' : 'BAD|';
$kept335 = $r335;
try { $r335 = new \stdClass(); } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 71 && $copy335->tag === 67 ? 'W|' : 'BAD|';
}
unset($error335);
try { $r335 = 127; } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 71 && $copy335->tag === 67 ? 'J|' : 'BAD|';
}
unset($error335);
$r335 = true;
echo $r335 === true && $s335 === true ? 'T|' : 'BAD|';
$s335 = false;
echo $r335 === false && $s335 === false ? 'L|' : 'BAD|';
$r335 = $kept335;
$read335 = $box335->v;
echo $read335 === $r335 && $kept335 === $s335 && $copy335->tag === 67 ? 'P|' : 'BAD|';
unset($read335);
unset($box335);
$s335 = 149;
echo $r335 === 149 && $copy335->tag === 67 && $kept335->tag === 71 ? 'F|' : 'BAD|';
$r335 = false;
$copy335 = 0;
$kept335 = 0;
unset($r335, $s335, $copy335, $kept335);
echo 'Z|';
