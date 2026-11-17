<?php
namespace Ns321LiteralBuiltinAllBuiltinsFalse;
class Box320 {
    public array|object|string|int|float|false|null $v = null {
        &get =>
            $this->v;
    }
    public function __destruct() { echo 'D|'; }
}
class Leaf320 { public $tag = 109; }
$box320 = new Box320();
$initial320 = $box320->v;
echo $initial320 === null ? 'I|' : 'BAD|';
unset($initial320);
$a320 =& $box320->v;
$b320 =& $box320->v;
echo $a320 === null && $b320 === $a320 ? 'N|' : 'BAD|';
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
$b320 = true;
echo $a320 === 1 && $b320 === $a320 ? 'B|' : 'BAD|';
$a320 = 17;
echo $a320 === 17 && $b320 === $a320 ? 'J|' : 'BAD|';
$b320 = 7.0;
echo $a320 === 7.0 && $b320 === $a320 ? 'D|' : 'BAD|';
$a320 = '12';
echo $a320 === '12' && $b320 === $a320 ? 'S|' : 'BAD|';
$b320 = null;
echo $a320 === null && $b320 === $a320 ? 'N|' : 'BAD|';
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
