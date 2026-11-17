<?php
declare(strict_types=1);
namespace I335P;
class A { public $tag = 61; }
class B { public $tag = 71; }
namespace I335C;
use I335P as Tree;
use I335P\A as Alpha;
class Box335 {
    public float|tReE\B|array|aLpHa|null $v {
        &get =>
            $this->{'v'};
    }
    public function __destruct() { echo 'D|'; }
}
namespace I335CX;
use stdClass as A;
use stdClass as B;
use stdClass as Tree;
use stdClass as Alpha;
$box335 = new \I335C\Box335();
$seed335 = new \I335P\A();
$box335->v = $seed335;
unset($seed335);
$r335 =& $box335->v;
$s335 =& $r335;
echo $r335 === $s335 && $r335->tag === 61 ? 'I|' : 'BAD|';
$copy335 = $box335->v;
$copy335->tag = 67;
echo $copy335 === $r335 && $r335 === $s335 && $r335->tag === 67 ? 'C|' : 'BAD|';
$s335 = new \I335P\B();
echo $r335 === $s335 && $r335->tag === 71 && $copy335->tag === 67 ? 'O1|' : 'BAD|';
$kept335 = $r335;
try { $r335 = new \stdClass(); } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 71 && $copy335->tag === 67 ? 'W|' : 'BAD|';
}
unset($error335);
try { $r335 = 'bad335'; } catch (\TypeError $error335) {
    echo $r335 === $s335 && $r335 === $kept335 && $r335->tag === 71 && $copy335->tag === 67 ? 'J|' : 'BAD|';
}
unset($error335);
$arrayseed335 = 3;
$r335 = [&$arrayseed335, [5]];
$arraycopy335 = $box335->v;
$s335[1][0] = 7;
$arrayseed335 = 11;
echo $r335[0] === 11 && $arraycopy335[0] === 11 && $r335[1][0] === 7 && $arraycopy335[1][0] === 5 ? 'A|' : 'BAD|';
$r335 = 3;
echo $r335 === 3.0 && $s335 === 3.0 ? 'V|' : 'BAD|';
$s335 = null;
echo $r335 === null && $s335 === null ? 'N|' : 'BAD|';
unset($arraycopy335, $arrayseed335);
$r335 = $kept335;
$read335 = $box335->v;
echo $read335 === $r335 && $kept335 === $s335 && $copy335->tag === 67 ? 'P|' : 'BAD|';
unset($read335);
unset($box335);
$s335 = false;
echo $r335 === false && $copy335->tag === 67 && $kept335->tag === 71 ? 'F|' : 'BAD|';
$r335 = false;
$copy335 = 0;
$kept335 = 0;
unset($r335, $s335, $copy335, $kept335);
echo 'Z|';
