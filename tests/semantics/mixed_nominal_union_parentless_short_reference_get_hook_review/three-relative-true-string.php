<?php
declare(strict_types=1);
namespace I335B;
class A { public $tag = 61; }
class B { public $tag = 71; }
class C { public $tag = 81; }
class Box335 {
    public namespace\C|true|A|string|namespace\B $v {
        &get =>
            $this->{'v'};
    }
    public function __destruct() { echo 'D|'; }
}
namespace I335BX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
$box335 = new \I335B\Box335();
$seed335 = new \I335B\A();
$box335->v = $seed335;
unset($seed335);
$r335 =& $box335->v;
$s335 =& $r335;
echo $r335 === $s335 && $r335->tag === 61 ? 'I|' : 'BAD|';
$copy335 = $box335->v;
$copy335->tag = 67;
echo $copy335 === $r335 && $r335 === $s335 && $r335->tag === 67 ? 'C|' : 'BAD|';
$s335 = new \I335B\B();
echo $r335 === $s335 && $r335->tag === 71 && $copy335->tag === 67 ? 'O1|' : 'BAD|';
$r335 = new \I335B\C();
echo $r335 === $s335 && $r335->tag === 81 && $copy335->tag === 67 ? 'O2|' : 'BAD|';
$kept335 = $r335;
try { $r335 = new \stdClass(); } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 81 && $copy335->tag === 67 ? 'W|' : 'BAD|';
}
unset($error335);
try { $r335 = 127; } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 81 && $copy335->tag === 67 ? 'J|' : 'BAD|';
}
unset($error335);
$r335 = true;
echo $r335 === true && $s335 === true ? 'T|' : 'BAD|';
$s335 = '12';
echo $r335 === '12' && $s335 === '12' ? 'S|' : 'BAD|';
$r335 = $kept335;
$read335 = $box335->v;
echo $read335 === $r335 && $kept335 === $s335 && $copy335->tag === 67 ? 'P|' : 'BAD|';
unset($read335);
unset($box335);
$s335 = 149;
echo $r335 === 149 && $copy335->tag === 67 && $kept335->tag === 81 ? 'F|' : 'BAD|';
$r335 = false;
$copy335 = 0;
$kept335 = 0;
unset($r335, $s335, $copy335, $kept335);
echo 'Z|';
