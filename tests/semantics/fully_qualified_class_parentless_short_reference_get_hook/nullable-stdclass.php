<?php
namespace Ns322NullableFullStd;
class Wrong320 { public $tag = 79; }
class Box320 {
    public ?\stdClass $v = null {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
$box320 = new Box320();
$initial320 = $box320->v;
echo $initial320 === null ? 'I|' : 'BAD|';
unset($initial320);
$a320 =& $box320->v;
$b320 =& $box320->v;
echo $a320 === null && $b320 === $a320 ? 'N|' : 'BAD|';
$a320 = new \stdClass();
$a320->tag = 61;
$copy320 = $box320->v;
$copy320->tag = 67;
echo $a320 === $copy320 && $b320 === $a320 && $a320->tag === 67 ? 'M|' : 'BAD|';
$b320 = new \stdClass();
$b320->tag = 71;
echo $a320 === $b320 && $a320 !== $copy320 && $a320->tag === 71 && $copy320->tag === 67 ? 'R|' : 'BAD|';
try { $a320 = new Wrong320(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign Ns322NullableFullStd\Wrong320 to reference held by property Ns322NullableFullStd\Box320::$v of type ?stdClass' && $a320 === $b320 && $a320->tag === 71 && $copy320->tag === 67 ? 'W|' : 'BAD|';
}
unset($e);
try { $b320 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns322NullableFullStd\Box320::$v of type ?stdClass' && $a320 === $b320 && $a320->tag === 71 && $copy320->tag === 67 ? 'A|' : 'BAD|';
}
unset($e);
try { $a320 = 127; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns322NullableFullStd\Box320::$v of type ?stdClass' && $a320 === $b320 && $a320->tag === 71 && $copy320->tag === 67 ? 'J|' : 'BAD|';
}
unset($e);
$a320 = null;
echo $a320 === null && $b320 === $a320 && $copy320->tag === 67 ? 'Q|' : 'BAD|';
$box320->v = new \stdClass();
$b320->tag = 73;
$kept320 = $a320;
$copyread320 = $box320->v;
echo $copyread320 === $a320 && $kept320 === $b320 && $copy320->tag === 67 ? 'P|' : 'BAD|';
unset($copyread320);
unset($box320);
$a320 = 149;
echo $b320 === 149 && $copy320->tag === 67 && $kept320->tag === 73 ? 'F|' : 'BAD|';
$a320 = [];
$copy320 = false;
$kept320 = false;
unset($a320, $b320, $copy320, $kept320);
echo 'Z|';
