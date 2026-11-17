<?php
declare(strict_types=0);
namespace Ns319WeakFloatBoolNullShortReference;
class Box319 {
    public float|bool|null $v {
        &get =>
            $this->v;
    }
}
$box319 = new Box319();
echo (array)$box319 === [] ? 'U|' : 'BAD|';
$copy319 = 'saved';
$copy319 = $box319->v;
echo $copy319 === null ? 'V|' : 'BAD|';
$copy319 = false;
$a319 =& $box319->v;
$b319 =& $box319->v;
echo $a319 === null && $b319 === null && $copy319 === false ? 'N|' : 'BAD|';
$a319 = 17;
echo $a319 === 17.0 && $b319 === 17.0 ? 'J|' : 'BAD|';
$b319 = true;
echo $a319 === true && $b319 === true ? 'T|' : 'BAD|';
$a319 = '12';
echo $a319 === 12.0 && $b319 === 12.0 ? 'S|' : 'BAD|';
$textcopy319 = $box319->v;
echo $textcopy319 === 12.0 && $a319 === 12.0 && $b319 === 12.0 ? 'Y|' : 'BAD|';
$textcopy319 = false;
unset($textcopy319);
$b319 = '2e0';
echo $a319 === 2.0 && $b319 === 2.0 ? 'X|' : 'BAD|';
$a319 = 'plain';
echo $a319 === true && $b319 === true ? 'Q|' : 'BAD|';
$b319 = '';
echo $a319 === false && $b319 === false ? 'E|' : 'BAD|';
$a319 = '0';
echo $a319 === 0.0 && $b319 === 0.0 ? 'C|' : 'BAD|';
$b319 = 7.0;
echo $a319 === 7.0 && $b319 === 7.0 ? 'F|' : 'BAD|';
$floatcopy319 = $box319->v;
echo $floatcopy319 === 7.0 && $a319 === 7.0 && $b319 === 7.0 ? 'D|' : 'BAD|';
$floatcopy319 = false;
unset($floatcopy319);
$a319 = false;
echo $a319 === false && $b319 === false ? 'B|' : 'BAD|';
$b319 = null;
echo $a319 === null && $b319 === null ? 'L|' : 'BAD|';
try { $b319 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns319WeakFloatBoolNullShortReference\Box319::$v of type float|bool|null' && $a319 === null && $b319 === null ? 'A|' : 'BAD|';
}
try { $a319 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns319WeakFloatBoolNullShortReference\Box319::$v of type float|bool|null' && $a319 === null && $b319 === null ? 'O|' : 'BAD|';
}
unset($e);
$b319 = 37;
echo $a319 === 37.0 && $b319 === 37.0 && $copy319 === false ? 'K|' : 'BAD|';
unset($box319);
$a319 = [];
echo $a319 === [] && $b319 === [] && $copy319 === false ? 'R|' : 'BAD|';
$copy319 = true;
unset($a319, $b319, $copy319);
echo 'Z|';
