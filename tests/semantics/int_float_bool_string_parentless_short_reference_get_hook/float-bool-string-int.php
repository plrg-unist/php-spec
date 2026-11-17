<?php
declare(strict_types=0);
namespace Ns316WeakFloatBoolStringIntShortReferenceAuthor;
class Box316 {
    public float|bool|string|int $v {
        &get =>
            $this->v;
    }
}
$box316 = new Box316();
echo (array)$box316 === [] ? 'U|' : 'BAD|';
$copy316 = 'saved';
try { $copy316 = $box316->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns316WeakFloatBoolStringIntShortReferenceAuthor\Box316::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy316 === 'saved' && (array)$box316 === [] ? 'P|' : 'BAD|';
unset($e);
$box316->v = 0;
$copy316 = $box316->v;
echo $copy316 === 0 ? 'V|' : 'BAD|';
$copy316 = 17;
$a316 =& $box316->v;
$b316 =& $box316->v;
echo $a316 === 0 && $b316 === 0 && $copy316 === 17 ? 'N|' : 'BAD|';
$a316 = 23;
echo $a316 === 23 && $b316 === 23 ? 'J|' : 'BAD|';
$a316 = 2.0;
echo $a316 === 2.0 && $b316 === 2.0 ? 'D|' : 'BAD|';
$probe_float316 = $box316->v;
echo $probe_float316 === 2.0 && $a316 === 2.0 && $b316 === 2.0 && $copy316 === 17 ? 'F|' : 'BAD|';
unset($probe_float316);
$b316 = true;
echo $a316 === true && $b316 === true ? 'T|' : 'BAD|';
$a316 = false;
echo $a316 === false && $b316 === false ? 'B|' : 'BAD|';
$probe_bool316 = $box316->v;
echo $probe_bool316 === false && $a316 === false && $b316 === false && $copy316 === 17 ? 'G|' : 'BAD|';
unset($probe_bool316);
$a316 = 'plain';
echo $a316 === 'plain' && $b316 === 'plain' ? 'P|' : 'BAD|';
$probe_string316 = $box316->v;
echo $probe_string316 === 'plain' && $a316 === 'plain' && $b316 === 'plain' && $copy316 === 17 ? 'H|' : 'BAD|';
unset($probe_string316);
$a316 = '12';
echo $a316 === '12' && $b316 === '12' ? 'S|' : 'BAD|';
$b316 = '12.5';
echo $a316 === '12.5' && $b316 === '12.5' ? 'L|' : 'BAD|';
$a316 = '2e0';
echo $a316 === '2e0' && $b316 === '2e0' ? 'X|' : 'BAD|';
$b316 = '';
echo $a316 === '' && $b316 === '' ? 'E|' : 'BAD|';
$a316 = '0';
echo $a316 === '0' && $b316 === '0' ? 'Q|' : 'BAD|';
$b316 = 2.0;
echo $a316 === 2.0 && $b316 === 2.0 ? 'W|' : 'BAD|';
try { $a316 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns316WeakFloatBoolStringIntShortReferenceAuthor\Box316::$v of type string|int|float|bool' && $a316 === 2.0 && $b316 === 2.0 ? 'U|' : 'BAD|';
}
try { $b316 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns316WeakFloatBoolStringIntShortReferenceAuthor\Box316::$v of type string|int|float|bool' && $a316 === 2.0 && $b316 === 2.0 ? 'A|' : 'BAD|';
}
try { $a316 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns316WeakFloatBoolStringIntShortReferenceAuthor\Box316::$v of type string|int|float|bool' && $a316 === 2.0 && $b316 === 2.0 ? 'O|' : 'BAD|';
}
unset($e);
$b316 = 37;
echo $a316 === 37 && $b316 === 37 && $copy316 === 17 ? 'K|' : 'BAD|';
unset($box316);
$a316 = null;
echo $a316 === null && $b316 === null && $copy316 === 17 ? 'R|' : 'BAD|';
unset($a316, $b316, $copy316);
echo 'Z|';
