<?php
declare(strict_types=1);
namespace Ns321StrictStringObjectFalseArray;
class Box320 {
    public string|OBJECT|false|ARRAY $v = false {
        &get =>
            $this->{'v'};
    }
    public function __destruct() { echo 'D|'; }
}
class Leaf320 { public $tag = 113; }
$box320 = new Box320();
$initial320 = $box320->v;
echo $initial320 === false ? 'I|' : 'BAD|';
unset($initial320);
$a320 =& $box320->v;
$b320 =& $box320->v;
echo $a320 === false && $b320 === $a320 ? 'N|' : 'BAD|';
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
$a320 = false;
echo $a320 === false && $b320 === $a320 ? 'F|' : 'BAD|';
try { $b320 = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns321StrictStringObjectFalseArray\Box320::$v of type object|array|string|false' && $a320 === false && $b320 === $a320 ? 'T|' : 'BAD|';
}
unset($e);
try { $a320 = 31; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns321StrictStringObjectFalseArray\Box320::$v of type object|array|string|false' && $a320 === false && $b320 === $a320 ? 'I|' : 'BAD|';
}
unset($e);
$b320 = '23';
echo $a320 === '23' && $b320 === $a320 ? 'S|' : 'BAD|';
$b320 = false;
echo $a320 === false && $b320 === $a320 ? 'B|' : 'BAD|';
try { $b320 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns321StrictStringObjectFalseArray\Box320::$v of type object|array|string|false' && $a320 === false && $b320 === $a320 ? 'N|' : 'BAD|';
}
unset($e);
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
