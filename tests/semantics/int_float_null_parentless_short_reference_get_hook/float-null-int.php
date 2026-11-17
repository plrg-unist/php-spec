<?php
declare(strict_types=0);
namespace Ns317WeakFloatNullIntShortReferenceAuthor;
class Box317 {
    public float|null|int $v {
        &get =>
            $this->v;
    }
}
$box317 = new Box317();
echo (array)$box317 === [] ? 'U|' : 'BAD|';
$copy317 = 'saved';
$copy317 = $box317->v;
echo $copy317 === null ? 'V|' : 'BAD|';
echo (array)$box317 === ['v' => null] ? 'P|' : 'BAD|';
$copy317 = false;
$a317 =& $box317->v;
$b317 =& $box317->v;
echo $a317 === null && $b317 === null && $copy317 === false ? 'N|' : 'BAD|';
$a317 = 17;
echo $a317 === 17 && $b317 === 17 ? 'J|' : 'BAD|';
$b317 = 2.0;
echo $a317 === 2.0 && $b317 === 2.0 ? 'D|' : 'BAD|';
$probe_float317 = $box317->v;
echo $probe_float317 === 2.0 && $a317 === 2.0 && $b317 === 2.0 && $copy317 === false ? 'G|' : 'BAD|';
unset($probe_float317);
$a317 = '12';
echo $a317 === 12 && $b317 === 12 ? 'S|' : 'BAD|';
$b317 = '12.5';
echo $a317 === 12.5 && $b317 === 12.5 ? 'Q|' : 'BAD|';
$a317 = '2e0';
echo $a317 === 2.0 && $b317 === 2.0 ? 'X|' : 'BAD|';
$b317 = true;
echo $a317 === 1 && $b317 === 1 ? 'T|' : 'BAD|';
$a317 = false;
echo $a317 === 0 && $b317 === 0 ? 'F|' : 'BAD|';
try { $b317 = 'bad'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns317WeakFloatNullIntShortReferenceAuthor\Box317::$v of type int|float|null' && $a317 === 0 && $b317 === 0 ? 'B|' : 'BAD|';
}
$a317 = null;
echo $a317 === null && $b317 === null ? 'L|' : 'BAD|';
$probe_null317 = $box317->v;
echo $probe_null317 === null && $a317 === null && $b317 === null && $copy317 === false ? 'H|' : 'BAD|';
unset($probe_null317);
try { $b317 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns317WeakFloatNullIntShortReferenceAuthor\Box317::$v of type int|float|null' && $a317 === null && $b317 === null ? 'A|' : 'BAD|';
}
try { $a317 = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns317WeakFloatNullIntShortReferenceAuthor\Box317::$v of type int|float|null' && $a317 === null && $b317 === null ? 'O|' : 'BAD|';
}
unset($e);
$b317 = 37;
echo $a317 === 37 && $b317 === 37 && $copy317 === false ? 'K|' : 'BAD|';
unset($box317);
$a317 = 'free';
echo $a317 === 'free' && $b317 === 'free' && $copy317 === false ? 'R|' : 'BAD|';
unset($a317, $b317, $copy317);
echo 'Z|';
