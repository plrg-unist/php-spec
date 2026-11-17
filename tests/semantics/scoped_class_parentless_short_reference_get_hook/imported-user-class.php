<?php
namespace Ns323Payload;
class Leaf320 { public $tag = 61; }
namespace Ns323Owner;
use Ns323Payload\Leaf320 as Target323;
class Box320 {
    public Target323 $v {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
namespace Ns323Consumer;
use stdClass as Target323;
$box320 = new \Ns323Owner\Box320();
$seed320 = new \Ns323Payload\Leaf320();
$seed320->tag = 61;
$box320->v = $seed320;
unset($seed320);
$initial320 = $box320->v;
echo $initial320 === $box320->v && $initial320->tag === 61 ? 'I|' : 'BAD|';
unset($initial320);
$a320 =& $box320->v;
$b320 =& $box320->v;
echo $a320 === $b320 && $a320->tag === 61 ? 'N|' : 'BAD|';
$copy320 = $box320->v;
$copy320->tag = 67;
echo $a320 === $copy320 && $b320 === $a320 && $a320->tag === 67 ? 'M|' : 'BAD|';
$b320 = new \Ns323Payload\Leaf320();
$b320->tag = 71;
echo $a320 === $b320 && $a320 !== $copy320 && $a320->tag === 71 && $copy320->tag === 67 ? 'R|' : 'BAD|';
try { $a320 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns323Owner\Box320::$v of type Ns323Payload\Leaf320' && $a320 === $b320 && $a320->tag === 71 && $copy320->tag === 67 ? 'W|' : 'BAD|';
}
unset($e);
try { $b320 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns323Owner\Box320::$v of type Ns323Payload\Leaf320' && $a320 === $b320 && $a320->tag === 71 && $copy320->tag === 67 ? 'A|' : 'BAD|';
}
unset($e);
try { $a320 = 127; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns323Owner\Box320::$v of type Ns323Payload\Leaf320' && $a320 === $b320 && $a320->tag === 71 && $copy320->tag === 67 ? 'J|' : 'BAD|';
}
unset($e);
try { $b320 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns323Owner\Box320::$v of type Ns323Payload\Leaf320' && $a320 === $b320 && $a320->tag === 71 && $copy320->tag === 67 ? 'Q|' : 'BAD|';
}
unset($e);
$kept320 = $a320;
$copyread320 = $box320->v;
echo $copyread320 === $a320 && $kept320 === $b320 && $copy320->tag === 67 ? 'P|' : 'BAD|';
unset($copyread320);
unset($box320);
$a320 = 149;
echo $b320 === 149 && $copy320->tag === 67 && $kept320->tag === 71 ? 'F|' : 'BAD|';
$a320 = [];
$copy320 = false;
$kept320 = false;
unset($a320, $b320, $copy320, $kept320);
echo 'Z|';
