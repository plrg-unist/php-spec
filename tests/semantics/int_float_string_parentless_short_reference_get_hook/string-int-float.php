<?php
declare(strict_types=0);
namespace Ns313WeakStringIntFloatShortReferenceAuthor;
class Box313 {
    public string|int|float $v = 0 {
        &get =>
            $this->v;
    }
}
$box313 = new Box313();
echo (array)$box313 === ['v' => 0] ? 'I|' : 'BAD|';
$copy313 = 'saved';
$copy313 = $box313->v;
echo $copy313 === 0 ? 'V|' : 'BAD|';
$copy313 = 17;
$a313 =& $box313->v;
$b313 =& $box313->v;
echo $a313 === 0 && $b313 === 0 && $copy313 === 17 ? 'N|' : 'BAD|';
$a313 = 23;
echo $a313 === 23 && $b313 === 23 ? 'J|' : 'BAD|';
$b313 = 2.5;
echo $a313 === 2.5 && $b313 === 2.5 ? 'D|' : 'BAD|';
$probe_float313 = $box313->v;
echo $probe_float313 === 2.5 && $a313 === 2.5 && $b313 === 2.5 && $copy313 === 17 ? 'G|' : 'BAD|';
unset($probe_float313);
$a313 = 'plain';
echo $a313 === 'plain' && $b313 === 'plain' ? 'P|' : 'BAD|';
$probe_string313 = $box313->v;
echo $probe_string313 === 'plain' && $a313 === 'plain' && $b313 === 'plain' && $copy313 === 17 ? 'H|' : 'BAD|';
unset($probe_string313);
$a313 = '12';
echo $a313 === '12' && $b313 === '12' ? 'S|' : 'BAD|';
$b313 = '12.5';
echo $a313 === '12.5' && $b313 === '12.5' ? 'L|' : 'BAD|';
$a313 = '2e0';
echo $a313 === '2e0' && $b313 === '2e0' ? 'X|' : 'BAD|';
$b313 = '';
echo $a313 === '' && $b313 === '' ? 'E|' : 'BAD|';
$a313 = '0';
echo $a313 === '0' && $b313 === '0' ? 'Q|' : 'BAD|';
$b313 = true;
echo $a313 === 1 && $b313 === 1 ? 'T|' : 'BAD|';
$a313 = false;
echo $a313 === 0 && $b313 === 0 ? 'F|' : 'BAD|';
try { $a313 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns313WeakStringIntFloatShortReferenceAuthor\Box313::$v of type string|int|float' && $a313 === 0 && $b313 === 0 ? 'U|' : 'BAD|';
}
try { $b313 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns313WeakStringIntFloatShortReferenceAuthor\Box313::$v of type string|int|float' && $a313 === 0 && $b313 === 0 ? 'A|' : 'BAD|';
}
try { $a313 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns313WeakStringIntFloatShortReferenceAuthor\Box313::$v of type string|int|float' && $a313 === 0 && $b313 === 0 ? 'O|' : 'BAD|';
}
unset($e);
$b313 = 37;
echo $a313 === 37 && $b313 === 37 && $copy313 === 17 ? 'K|' : 'BAD|';
unset($box313);
$a313 = true;
echo $a313 === true && $b313 === true && $copy313 === 17 ? 'R|' : 'BAD|';
unset($a313, $b313, $copy313);
echo 'Z|';
