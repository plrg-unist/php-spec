<?php
namespace W340B;
interface A {}
interface B {}
class Payload340 implements \W340B\A,\W340B\B { public $tag = 61; }
class Partial340 implements \W340B\A { public $tag = 81; }
class Box340 {
    public array|(namespace\B&A)|null $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace W340BX;
use stdClass as A;
use stdClass as B;
use stdClass as C;
use stdClass as Tree;
use stdClass as Alpha;
$box340 = new \W340B\Box340();
$seed340 = new \W340B\Payload340();
$box340->v = $seed340;
unset($seed340);
$r340 =& $box340->v;
$s340 =& $r340;
echo $r340 === $s340 && $r340->tag === 61 ? 'I|' : 'BAD|';
$copy340 = $box340->v;
$copy340->tag = 67;
echo $copy340 === $r340 && $r340 === $s340 && $r340->tag === 67 ? 'C|' : 'BAD|';
$s340 = new \W340B\Payload340();
$s340->tag = 71;
echo $r340 === $s340 && $r340->tag === 71 && $copy340->tag === 67 ? 'O1|' : 'BAD|';
$kept340 = $r340;
try { $r340 = new \W340B\Partial340(); } catch (\TypeError $error340) {
    echo $r340 === $s340 && $r340 === $kept340 && $r340->tag === 71 && $copy340->tag === 67 ? 'W|' : 'BAD|';
}
unset($error340);
try { $r340 = 127; } catch (\TypeError $error340) {
    echo $r340 === $s340 && $r340 === $kept340 && $r340->tag === 71 && $copy340->tag === 67 ? 'J|' : 'BAD|';
}
unset($error340);
$arrayseed340 = 3;
$r340 = [&$arrayseed340, [5]];
$arraycopy340 = $box340->v;
$s340[1][0] = 7;
$arrayseed340 = 11;
echo $r340[0] === 11 && $arraycopy340[0] === 11 && $r340[1][0] === 7 && $arraycopy340[1][0] === 5 ? 'A|' : 'BAD|';
$s340 = null;
echo $r340 === null && $s340 === null ? 'N|' : 'BAD|';
unset($arraycopy340, $arrayseed340);
$r340 = $kept340;
$read340 = $box340->v;
echo $read340 === $r340 && $kept340 === $s340 && $copy340->tag === 67 ? 'P|' : 'BAD|';
unset($read340);
unset($box340);
$s340 = 149;
echo $r340 === 149 && $copy340->tag === 67 && $kept340->tag === 71 ? 'F|' : 'BAD|';
$r340 = false;
$copy340 = 0;
$kept340 = 0;
unset($r340, $s340, $copy340, $kept340);
echo 'Z|';
