<?php
declare(strict_types=0);
namespace Ns312WeakIntFloatBoolShortReferenceAuthor;
class Box312 {
    public int|float|bool $v = 0 {
        &get =>
            $this->v;
    }
}
$box312 = new Box312();
echo (array)$box312 === ['v' => 0] ? 'I|' : 'BAD|';
$copy312 = 'saved';
$copy312 = $box312->v;
echo $copy312 === 0 ? 'V|' : 'BAD|';
$copy312 = 17;
$a312 =& $box312->v;
$b312 =& $box312->v;
echo $a312 === 0 && $b312 === 0 && $copy312 === 17 ? 'N|' : 'BAD|';
$a312 = 23;
echo $a312 === 23 && $b312 === 23 ? 'J|' : 'BAD|';
$b312 = 2.5;
echo $a312 === 2.5 && $b312 === 2.5 ? 'D|' : 'BAD|';
$probe_float312 = $box312->v;
echo $probe_float312 === 2.5 && $a312 === 2.5 && $b312 === 2.5 && $copy312 === 17 ? 'G|' : 'BAD|';
unset($probe_float312);
$a312 = true;
echo $a312 === true && $b312 === true ? 'T|' : 'BAD|';
$b312 = false;
echo $a312 === false && $b312 === false ? 'F|' : 'BAD|';
$probe_bool312 = $box312->v;
echo $probe_bool312 === false && $a312 === false && $b312 === false && $copy312 === 17 ? 'H|' : 'BAD|';
unset($probe_bool312);
$a312 = '12';
echo $a312 === 12 && $b312 === 12 ? 'S|' : 'BAD|';
$b312 = '12.5';
echo $a312 === 12.5 && $b312 === 12.5 ? 'L|' : 'BAD|';
$a312 = '2e0';
echo $a312 === 2.0 && $b312 === 2.0 ? 'X|' : 'BAD|';
$b312 = 'plain';
echo $a312 === true && $b312 === true ? 'P|' : 'BAD|';
$a312 = '';
echo $a312 === false && $b312 === false ? 'E|' : 'BAD|';
$b312 = '0';
echo $a312 === 0 && $b312 === 0 ? 'Q|' : 'BAD|';
try { $a312 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns312WeakIntFloatBoolShortReferenceAuthor\Box312::$v of type int|float|bool' && $a312 === 0 && $b312 === 0 ? 'U|' : 'BAD|';
}
try { $b312 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns312WeakIntFloatBoolShortReferenceAuthor\Box312::$v of type int|float|bool' && $a312 === 0 && $b312 === 0 ? 'A|' : 'BAD|';
}
try { $a312 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns312WeakIntFloatBoolShortReferenceAuthor\Box312::$v of type int|float|bool' && $a312 === 0 && $b312 === 0 ? 'O|' : 'BAD|';
}
unset($e);
$b312 = 37;
echo $a312 === 37 && $b312 === 37 && $copy312 === 17 ? 'K|' : 'BAD|';
unset($box312);
$a312 = 'detached';
echo $a312 === 'detached' && $b312 === 'detached' && $copy312 === 17 ? 'R|' : 'BAD|';
unset($a312, $b312, $copy312);
echo 'Z|';
