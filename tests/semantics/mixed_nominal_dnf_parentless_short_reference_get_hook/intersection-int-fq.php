<?php
namespace W340A;
interface A {}
interface B {}
class Payload340 implements \W340A\A,\W340A\B { public $tag = 61; }
class Partial340 implements \W340A\A { public $tag = 81; }
class Box340 {
    public (\W340A\A&\W340A\B)|int $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W340AX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
use stdClass as Tree;
use stdClass as Alpha;
$box340 = new \W340A\Box340();
$seed340 = new \W340A\Payload340();
$box340->v = $seed340;
unset($seed340);
$r340 =& $box340->v;
$s340 =& $r340;
echo $r340 === $s340 && $r340->tag === 61 ? 'I|' : 'BAD|';
$copy340 = $box340->v;
$copy340->tag = 67;
echo $copy340 === $r340 && $r340 === $s340 && $r340->tag === 67 ? 'C|' : 'BAD|';
$s340 = new \W340A\Payload340();
$s340->tag = 71;
echo $r340 === $s340 && $r340->tag === 71 && $copy340->tag === 67 ? 'O1|' : 'BAD|';
$kept340 = $r340;
try { $r340 = new \W340A\Partial340(); } catch (\TypeError $error340) {
    echo $r340 === $s340 && $r340 === $kept340 && $r340->tag === 71 && $copy340->tag === 67 ? 'W|' : 'BAD|';
}
unset($error340);
try { $r340 = []; } catch (\TypeError $error340) {
    echo $r340 === $s340 && $r340 === $kept340 && $r340->tag === 71 && $copy340->tag === 67 ? 'J|' : 'BAD|';
}
unset($error340);
$r340 = '127';
echo $r340 === 127 && $s340 === 127 ? 'N|' : 'BAD|';
$s340 = true;
echo $r340 === 1 && $s340 === 1 ? 'B|' : 'BAD|';
$r340 = $kept340;
$read340 = $box340->v;
echo $read340 === $r340 && $kept340 === $s340 && $copy340->tag === 67 ? 'P|' : 'BAD|';
unset($read340);
unset($box340);
$s340 = [];
echo $r340 === [] && $copy340->tag === 67 && $kept340->tag === 71 ? 'F|' : 'BAD|';
$r340 = false;
$copy340 = 0;
$kept340 = 0;
unset($r340, $s340, $copy340, $kept340);
echo 'Z|';
