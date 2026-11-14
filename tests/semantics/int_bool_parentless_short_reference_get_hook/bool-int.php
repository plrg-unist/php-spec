<?php
declare(strict_types=0);
namespace Ns309WeakBoolIntShortReferenceAuthor;
class Box309 {
    public bool|int $v {
        &get =>
            $this->v;
    }
}
$box309 = new Box309();
echo (array)$box309 === [] ? 'U|' : 'BAD|';
$copy309 = 'saved';
try { $copy309 = $box309->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns309WeakBoolIntShortReferenceAuthor\Box309::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy309 === 'saved' && (array)$box309 === [] ? 'P|' : 'BAD|';
unset($e);
$box309->v = 0;
$copy309 = $box309->v;
echo $copy309 === 0 ? 'V|' : 'BAD|';
$copy309 = false;
$a309 =& $box309->v;
$b309 =& $box309->v;
echo $a309 === 0 && $b309 === 0 && $copy309 === false ? 'N|' : 'BAD|';
$a309 = 17;
echo $b309 === 17 ? 'J|' : 'BAD|';
$b309 = true;
echo $a309 === true && $b309 === true ? 'T|' : 'BAD|';
$a309 = false;
echo $a309 === false && $b309 === false ? 'F|' : 'BAD|';
$b309 = 2.0;
echo $a309 === 2 && $b309 === 2 ? 'D|' : 'BAD|';
$a309 = '12';
echo $a309 === 12 && $b309 === 12 ? 'S|' : 'BAD|';
$b309 = 'plain';
echo $a309 === true && $b309 === true ? 'P|' : 'BAD|';
$a309 = '';
echo $a309 === false && $b309 === false ? 'E|' : 'BAD|';
$b309 = '0';
echo $a309 === 0 && $b309 === 0 ? 'Q|' : 'BAD|';
try { $a309 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns309WeakBoolIntShortReferenceAuthor\Box309::$v of type int|bool' && $a309 === 0 && $b309 === 0 ? 'L|' : 'BAD|';
}
try { $b309 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns309WeakBoolIntShortReferenceAuthor\Box309::$v of type int|bool' && $a309 === 0 && $b309 === 0 ? 'A|' : 'BAD|';
}
try { $a309 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns309WeakBoolIntShortReferenceAuthor\Box309::$v of type int|bool' && $a309 === 0 && $b309 === 0 ? 'O|' : 'BAD|';
}
unset($e);
$b309 = 37;
echo $a309 === 37 && $copy309 === false ? 'K|' : 'BAD|';
unset($box309);
$a309 = 3.5;
echo $b309 === 3.5 && $copy309 === false ? 'R|' : 'BAD|';
unset($a309, $b309, $copy309);
echo 'Z|';
