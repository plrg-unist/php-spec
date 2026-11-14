<?php
namespace Ns304WeakOmittedNullShortReference;
class Box304 {
    public null $v {
        &get =>
            $this->v;
    }
}
$box304 = new Box304();
echo (array)$box304 === [] ? 'U|' : 'BAD|';
$copy304 = $box304->v;
echo $copy304 === null && (array)$box304 === ['v' => null] ? 'V|' : 'BAD|';
$copy304 = false;
echo $copy304 === false ? 'C|' : 'BAD|';
$a304 =& $box304->v;
$b304 =& $box304->v;
echo $a304 === null && $b304 === null && $box304->v === null ? 'N|' : 'BAD|';
try { $a304 = false; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign false to reference held by property Ns304WeakOmittedNullShortReference\Box304::$v of type null' ? 'F|' : 'BAD|';
}
try { $b304 = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns304WeakOmittedNullShortReference\Box304::$v of type null' ? 'T|' : 'BAD|';
}
try { $a304 = 0; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns304WeakOmittedNullShortReference\Box304::$v of type null' ? '0|' : 'BAD|';
}
try { $b304 = 'free'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns304WeakOmittedNullShortReference\Box304::$v of type null' ? 'S|' : 'BAD|';
}
try { $a304 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns304WeakOmittedNullShortReference\Box304::$v of type null' ? 'A|' : 'BAD|';
}
unset($e);
echo $a304 === null && $b304 === null && $copy304 === false ? 'K|' : 'BAD|';
unset($box304);
$a304 = 37;
echo $a304 === 37 && $b304 === 37 && $copy304 === false ? 'R|' : 'BAD|';
unset($a304, $b304, $copy304);
echo 'Z|';
