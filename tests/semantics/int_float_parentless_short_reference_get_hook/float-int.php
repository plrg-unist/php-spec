<?php
declare(strict_types=0);
namespace Ns307WeakFloatIntShortReferenceAuthor;
class Box307 {
    public float|int $v {
        &get =>
            $this->v;
    }
}
$box307 = new Box307();
echo (array)$box307 === [] ? 'U|' : 'BAD|';
$copy307 = 'saved';
try { $copy307 = $box307->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns307WeakFloatIntShortReferenceAuthor\Box307::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy307 === 'saved' && (array)$box307 === [] ? 'P|' : 'BAD|';
unset($e);
$box307->v = 0;
$copy307 = $box307->v;
echo $copy307 === 0 ? 'V|' : 'BAD|';
$copy307 = false;
$a307 =& $box307->v;
$b307 =& $box307->v;
echo $a307 === 0 && $b307 === 0 && $copy307 === false ? 'N|' : 'BAD|';
$a307 = 17;
echo $b307 === 17 ? 'J|' : 'BAD|';
$b307 = 2.0;
echo $a307 === 2.0 ? 'D|' : 'BAD|';
$a307 = '12';
echo $a307 === 12 && $b307 === 12 ? 'S|' : 'BAD|';
$b307 = '12.5';
echo $a307 === 12.5 && $b307 === 12.5 ? 'Q|' : 'BAD|';
$a307 = '2e0';
echo $a307 === 2.0 && $b307 === 2.0 ? 'X|' : 'BAD|';
$b307 = true;
echo $a307 === 1 && $b307 === 1 ? 'T|' : 'BAD|';
$a307 = false;
echo $a307 === 0 && $b307 === 0 ? 'F|' : 'BAD|';
try { $b307 = 'bad'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns307WeakFloatIntShortReferenceAuthor\Box307::$v of type int|float' && $a307 === 0 && $b307 === 0 ? 'B|' : 'BAD|';
}
try { $a307 = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns307WeakFloatIntShortReferenceAuthor\Box307::$v of type int|float' && $a307 === 0 && $b307 === 0 ? 'L|' : 'BAD|';
}
try { $b307 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns307WeakFloatIntShortReferenceAuthor\Box307::$v of type int|float' && $a307 === 0 && $b307 === 0 ? 'A|' : 'BAD|';
}
try { $a307 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns307WeakFloatIntShortReferenceAuthor\Box307::$v of type int|float' && $a307 === 0 && $b307 === 0 ? 'O|' : 'BAD|';
}
unset($e);
$b307 = 37;
echo $a307 === 37 && $copy307 === false ? 'K|' : 'BAD|';
unset($box307);
$a307 = false;
echo $b307 === false && $copy307 === false ? 'R|' : 'BAD|';
unset($a307, $b307, $copy307);
echo 'Z|';
