<?php
declare(strict_types=0);
namespace Ns310WeakFloatBoolShortReferenceAuthor;
class Box310 {
    public float|bool $v = 0.0 {
        &get =>
            $this->v;
    }
}
$box310 = new Box310();
echo (array)$box310 === ['v' => 0.0] ? 'I|' : 'BAD|';
$copy310 = 'saved';
$copy310 = $box310->v;
echo $copy310 === 0.0 ? 'V|' : 'BAD|';
$copy310 = false;
$a310 =& $box310->v;
$b310 =& $box310->v;
echo $a310 === 0.0 && $b310 === 0.0 && $copy310 === false ? 'N|' : 'BAD|';
$a310 = 17;
echo $b310 === 17.0 ? 'J|' : 'BAD|';
$b310 = 2.0;
echo $a310 === 2.0 && $b310 === 2.0 ? 'D|' : 'BAD|';
$b310 = true;
echo $a310 === true && $b310 === true ? 'T|' : 'BAD|';
$a310 = false;
echo $a310 === false && $b310 === false ? 'F|' : 'BAD|';
$a310 = '12';
echo $a310 === 12.0 && $b310 === 12.0 ? 'S|' : 'BAD|';
$b310 = '12.5';
echo $a310 === 12.5 && $b310 === 12.5 ? 'H|' : 'BAD|';
$b310 = 'plain';
echo $a310 === true && $b310 === true ? 'P|' : 'BAD|';
$a310 = '';
echo $a310 === false && $b310 === false ? 'E|' : 'BAD|';
$b310 = '0';
echo $a310 === 0.0 && $b310 === 0.0 ? 'Q|' : 'BAD|';
try { $a310 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns310WeakFloatBoolShortReferenceAuthor\Box310::$v of type float|bool' && $a310 === 0.0 && $b310 === 0.0 ? 'L|' : 'BAD|';
}
try { $b310 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns310WeakFloatBoolShortReferenceAuthor\Box310::$v of type float|bool' && $a310 === 0.0 && $b310 === 0.0 ? 'A|' : 'BAD|';
}
try { $a310 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns310WeakFloatBoolShortReferenceAuthor\Box310::$v of type float|bool' && $a310 === 0.0 && $b310 === 0.0 ? 'O|' : 'BAD|';
}
unset($e);
$b310 = 37;
echo $a310 === 37.0 && $copy310 === false ? 'K|' : 'BAD|';
unset($box310);
$a310 = 23;
echo $b310 === 23 && $copy310 === false ? 'R|' : 'BAD|';
unset($a310, $b310, $copy310);
echo 'Z|';
