<?php
declare(strict_types=1);
namespace Ns321StrictAllBuiltinsTrueReverse;
class Box320 {
    public NULL|TRUE|float|OBJECT|string|ARRAY|int $v = null {
        &get =>
            $this->{'v'};
    }
    public function __destruct() { echo 'D|'; }
}
class Leaf320 { public $tag = 113; }
$box320 = new Box320();
$initial320 = $box320->v;
echo $initial320 === null ? 'I|' : 'BAD|';
unset($initial320);
$a320 =& $box320->v;
$b320 =& $box320->v;
echo $a320 === null && $b320 === $a320 ? 'N|' : 'BAD|';
$seed320 = 73;
$a320 = [&$seed320, [79]];
$copyarray320 = $box320->v;
$a320[1][0] = 83;
$seed320 = 'peer';
echo $copyarray320 === ['peer', [79]] && $a320 === ['peer', [83]] ? 'C|' : 'BAD|';
$a320 = new \stdClass();
$a320->tag = 89;
$copyobject320 = $box320->v;
$copyobject320->tag = 97;
echo $a320 === $copyobject320 && $a320->tag === 97 ? 'M|' : 'BAD|';
$b320 = new Leaf320();
echo $box320->v === $b320 && $b320 !== $copyobject320 && $b320->tag === 113 && $copyobject320->tag === 97 ? 'L|' : 'BAD|';
$a320 = true;
echo $a320 === true && $b320 === $a320 ? 'T|' : 'BAD|';
try { $b320 = false; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign false to reference held by property Ns321StrictAllBuiltinsTrueReverse\Box320::$v of type object|array|string|int|float|true|null' && $a320 === true && $b320 === $a320 ? 'F|' : 'BAD|';
}
unset($e);
$a320 = 31;
echo $a320 === 31 && $b320 === $a320 ? 'J|' : 'BAD|';
$b320 = 5.0;
echo $a320 === 5.0 && $b320 === $a320 ? 'D|' : 'BAD|';
$a320 = '18';
echo $a320 === '18' && $b320 === $a320 ? 'S|' : 'BAD|';
$b320 = null;
echo $a320 === null && $b320 === $a320 ? 'N|' : 'BAD|';
$a320 = new Leaf320();
$kept320 = $a320;
$copyread320 = $box320->v;
echo $copyread320 === $a320 && $kept320 === $b320 && $copyobject320->tag === 97 ? 'P|' : 'BAD|';
unset($copyread320);
unset($box320);
$a320 = 157;
echo $b320 === 157 && $copyobject320->tag === 97 && $kept320->tag === 113 && $copyarray320 === ['peer', [79]] ? 'R|' : 'BAD|';
$a320 = [];
$copyarray320 = false;
$copyobject320 = false;
$kept320 = false;
unset($a320, $b320, $copyarray320, $copyobject320, $kept320, $seed320);
echo 'Z|';
