<?php
declare(strict_types=0);
namespace Ns308WeakStringFloatShortReferenceAuthor;
class Box308 {
    public string|float $v {
        &get =>
            $this->v;
    }
}
$box308 = new Box308();
echo (array)$box308 === [] ? 'U|' : 'BAD|';
$copy308 = 'saved';
try { $copy308 = $box308->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns308WeakStringFloatShortReferenceAuthor\Box308::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy308 === 'saved' && (array)$box308 === [] ? 'P|' : 'BAD|';
unset($e);
$box308->v = 0.0;
$copy308 = $box308->v;
echo $copy308 === 0.0 ? 'V|' : 'BAD|';
$copy308 = false;
$a308 =& $box308->v;
$b308 =& $box308->v;
echo $a308 === 0.0 && $b308 === 0.0 && $copy308 === false ? 'N|' : 'BAD|';
$a308 = 2.0;
echo $b308 === 2.0 ? 'D|' : 'BAD|';
$b308 = '12';
echo $a308 === '12' && $b308 === '12' ? 'S|' : 'BAD|';
$a308 = 'plain';
echo $a308 === 'plain' && $b308 === 'plain' ? 'P|' : 'BAD|';
$b308 = 17;
echo $a308 === 17.0 && $b308 === 17.0 ? 'J|' : 'BAD|';
$a308 = true;
echo $a308 === 1.0 && $b308 === 1.0 ? 'T|' : 'BAD|';
$b308 = false;
echo $a308 === 0.0 && $b308 === 0.0 ? 'F|' : 'BAD|';
try { $a308 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns308WeakStringFloatShortReferenceAuthor\Box308::$v of type string|float' && $a308 === 0.0 && $b308 === 0.0 ? 'L|' : 'BAD|';
}
try { $b308 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns308WeakStringFloatShortReferenceAuthor\Box308::$v of type string|float' && $a308 === 0.0 && $b308 === 0.0 ? 'A|' : 'BAD|';
}
try { $a308 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns308WeakStringFloatShortReferenceAuthor\Box308::$v of type string|float' && $a308 === 0.0 && $b308 === 0.0 ? 'O|' : 'BAD|';
}
unset($e);
$b308 = 'kept';
echo $a308 === 'kept' && $copy308 === false ? 'K|' : 'BAD|';
unset($box308);
$a308 = false;
echo $b308 === false && $copy308 === false ? 'R|' : 'BAD|';
unset($a308, $b308, $copy308);
echo 'Z|';
