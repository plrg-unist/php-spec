<?php
namespace W335B;
class A { public $tag = 61; }
class B { public $tag = 71; }
class Box335 {
    public array|namespace\B|null|A $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W335BX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
use stdClass as Tree;
use stdClass as Alpha;
$box335 = new \W335B\Box335();
$seed335 = new \W335B\A();
$box335->v = $seed335;
unset($seed335);
$r335 =& $box335->v;
$s335 =& $r335;
echo $r335 === $s335 && $r335->tag === 61 ? 'I|' : 'BAD|';
$copy335 = $box335->v;
$copy335->tag = 67;
echo $copy335 === $r335 && $r335 === $s335 && $r335->tag === 67 ? 'C|' : 'BAD|';
$s335 = new \W335B\B();
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
$arrayseed335 = 3;
$r335 = [&$arrayseed335, [5]];
$arraycopy335 = $box335->v;
$s335[1][0] = 7;
$arrayseed335 = 11;
echo $r335[0] === 11 && $arraycopy335[0] === 11 && $r335[1][0] === 7 && $arraycopy335[1][0] === 5 ? 'A|' : 'BAD|';
$s335 = null;
echo $r335 === null && $s335 === null ? 'N|' : 'BAD|';
unset($arraycopy335, $arrayseed335);
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
