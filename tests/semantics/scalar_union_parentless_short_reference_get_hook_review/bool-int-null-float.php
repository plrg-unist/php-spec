<?php
declare(strict_types=1);
namespace Ns319StrictBoolIntNullFloatShortReference;
class Box319 {
    public BOOL|int|NULL|float $v = 0 {
        &get =>
            $this->{'v'};
    }
}
$box319 = new Box319();
echo (array)$box319 === ['v' => 0] ? 'I|' : 'BAD|';
$copy319 = 'saved';
$copy319 = $box319->v;
echo $copy319 === 0 ? 'V|' : 'BAD|';
$copy319 = false;
$a319 =& $box319->v;
$b319 =& $box319->v;
echo $a319 === 0 && $b319 === 0 && $copy319 === false ? 'N|' : 'BAD|';
$a319 = 17;
echo $a319 === 17 && $b319 === 17 ? 'J|' : 'BAD|';
$b319 = true;
echo $a319 === true && $b319 === true ? 'T|' : 'BAD|';
try { $a319 = '12'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns319StrictBoolIntNullFloatShortReference\Box319::$v of type int|float|bool|null' && $a319 === true && $b319 === true ? 'S|' : 'BAD|';
}
$textcopy319 = $box319->v;
echo $textcopy319 === true && $a319 === true && $b319 === true ? 'Y|' : 'BAD|';
$textcopy319 = false;
unset($textcopy319);
try { $b319 = '2e0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns319StrictBoolIntNullFloatShortReference\Box319::$v of type int|float|bool|null' && $a319 === true && $b319 === true ? 'X|' : 'BAD|';
}
try { $a319 = 'plain'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns319StrictBoolIntNullFloatShortReference\Box319::$v of type int|float|bool|null' && $a319 === true && $b319 === true ? 'Q|' : 'BAD|';
}
try { $b319 = ''; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns319StrictBoolIntNullFloatShortReference\Box319::$v of type int|float|bool|null' && $a319 === true && $b319 === true ? 'E|' : 'BAD|';
}
try { $a319 = '0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns319StrictBoolIntNullFloatShortReference\Box319::$v of type int|float|bool|null' && $a319 === true && $b319 === true ? 'C|' : 'BAD|';
}
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
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns319StrictBoolIntNullFloatShortReference\Box319::$v of type int|float|bool|null' && $a319 === null && $b319 === null ? 'A|' : 'BAD|';
}
try { $a319 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns319StrictBoolIntNullFloatShortReference\Box319::$v of type int|float|bool|null' && $a319 === null && $b319 === null ? 'O|' : 'BAD|';
}
unset($e);
$b319 = 37;
echo $a319 === 37 && $b319 === 37 && $copy319 === false ? 'K|' : 'BAD|';
unset($box319);
$a319 = [];
echo $a319 === [] && $b319 === [] && $copy319 === false ? 'R|' : 'BAD|';
$copy319 = true;
unset($a319, $b319, $copy319);
echo 'Z|';
