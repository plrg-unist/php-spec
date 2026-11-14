<?php
declare(strict_types=0);
namespace Ns311WeakBoolStringShortReferenceAuthor;
class Box311 {
    public bool|string $v = false {
        &get =>
            $this->v;
    }
}
$box311 = new Box311();
echo (array)$box311 === ['v' => false] ? 'I|' : 'BAD|';
$copy311 = 'saved';
$copy311 = $box311->v;
echo $copy311 === false ? 'V|' : 'BAD|';
$copy311 = 17;
$a311 =& $box311->v;
$b311 =& $box311->v;
echo $a311 === false && $b311 === false && $copy311 === 17 ? 'N|' : 'BAD|';
$a311 = true;
echo $a311 === true && $b311 === true ? 'T|' : 'BAD|';
$b311 = false;
echo $a311 === false && $b311 === false ? 'F|' : 'BAD|';
$a311 = 'plain';
echo $a311 === 'plain' && $b311 === 'plain' ? 'P|' : 'BAD|';
$b311 = '12';
echo $a311 === '12' && $b311 === '12' ? 'S|' : 'BAD|';
$a311 = '12.5';
echo $a311 === '12.5' && $b311 === '12.5' ? 'H|' : 'BAD|';
$b311 = '';
echo $a311 === '' && $b311 === '' ? 'E|' : 'BAD|';
$a311 = '0';
echo $a311 === '0' && $b311 === '0' ? 'Q|' : 'BAD|';
$probe311 = $box311->v;
echo $probe311 === '0' && $a311 === '0' && $b311 === '0' && $copy311 === 17 ? 'G|' : 'BAD|';
unset($probe311);
$a311 = 17;
echo $a311 === '17' && $b311 === '17' ? 'J|' : 'BAD|';
$b311 = 2.5;
echo $a311 === '2.5' && $b311 === '2.5' ? 'D|' : 'BAD|';
try { $a311 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns311WeakBoolStringShortReferenceAuthor\Box311::$v of type string|bool' && $a311 === '2.5' && $b311 === '2.5' ? 'L|' : 'BAD|';
}
try { $b311 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns311WeakBoolStringShortReferenceAuthor\Box311::$v of type string|bool' && $a311 === '2.5' && $b311 === '2.5' ? 'A|' : 'BAD|';
}
try { $a311 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns311WeakBoolStringShortReferenceAuthor\Box311::$v of type string|bool' && $a311 === '2.5' && $b311 === '2.5' ? 'O|' : 'BAD|';
}
unset($e);
$b311 = 'kept';
echo $a311 === 'kept' && $b311 === 'kept' && $copy311 === 17 ? 'K|' : 'BAD|';
unset($box311);
$a311 = 23;
echo $a311 === 23 && $b311 === 23 && $copy311 === 17 ? 'R|' : 'BAD|';
unset($a311, $b311, $copy311);
echo 'Z|';
