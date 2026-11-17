<?php
namespace Ns321LiteralBuiltinArrayObjectFalse;
class Box320 {
    public array|object|false $v = false {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
class Leaf320 { public $tag = 109; }
$box320 = new Box320();
$initial320 = $box320->v;
echo $initial320 === false ? 'I|' : 'BAD|';
unset($initial320);
$a320 =& $box320->v;
$b320 =& $box320->v;
echo $a320 === false && $b320 === $a320 ? 'N|' : 'BAD|';
$seed320 = 61;
$a320 = [&$seed320, [67]];
$copyarray320 = $box320->v;
$a320[1][0] = 71;
$seed320 = 'leaf';
echo $copyarray320 === ['leaf', [67]] && $a320 === ['leaf', [71]] ? 'C|' : 'BAD|';
$a320 = new \stdClass();
$a320->tag = 103;
$copyobject320 = $box320->v;
$copyobject320->tag = 107;
echo $a320 === $copyobject320 && $a320->tag === 107 ? 'M|' : 'BAD|';
$b320 = new Leaf320();
echo $box320->v === $b320 && $b320 !== $copyobject320 && $b320->tag === 109 && $copyobject320->tag === 107 ? 'L|' : 'BAD|';
$a320 = false;
echo $a320 === false && $b320 === $a320 ? 'F|' : 'BAD|';
try { $b320 = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns321LiteralBuiltinArrayObjectFalse\Box320::$v of type object|array|false' ? 'T|' : 'BAD|';
}
unset($e);
try { $a320 = 127; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns321LiteralBuiltinArrayObjectFalse\Box320::$v of type object|array|false' ? 'I|' : 'BAD|';
}
unset($e);
try { $b320 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns321LiteralBuiltinArrayObjectFalse\Box320::$v of type object|array|false' ? 'N|' : 'BAD|';
}
unset($e);
$a320 = new Leaf320();
$kept320 = $a320;
$copyread320 = $box320->v;
echo $copyread320 === $a320 && $kept320 === $b320 && $copyobject320->tag === 107 ? 'P|' : 'BAD|';
unset($copyread320);
unset($box320);
$a320 = 149;
echo $b320 === 149 && $copyobject320->tag === 107 && $kept320->tag === 109 && $copyarray320 === ['leaf', [67]] ? 'R|' : 'BAD|';
$a320 = [];
$copyarray320 = false;
$copyobject320 = false;
$kept320 = false;
unset($a320, $b320, $copyarray320, $copyobject320, $kept320, $seed320);
echo 'Z|';
