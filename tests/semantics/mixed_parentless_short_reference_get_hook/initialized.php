<?php
namespace Ns305WeakInitializedMixedShortReference;
class Box305 {
    public mixed $v = null {
        &get =>
            $this->v;
    }
}
$box305 = new Box305();
echo (array)$box305 === ['v' => null] ? 'I|' : 'BAD|';
$copy305 = $box305->v;
echo $copy305 === null && (array)$box305 === ['v' => null] ? 'V|' : 'BAD|';
$copy305 = false;
echo $copy305 === false ? 'C|' : 'BAD|';
$a305 =& $box305->v;
$b305 =& $box305->v;
echo $a305 === null && $b305 === null && $box305->v === null ? 'N|' : 'BAD|';
$a305 = false;
echo $b305 === false ? 'F|' : 'BAD|';
$b305 = true;
echo $a305 === true ? 'T|' : 'BAD|';
$a305 = 0;
echo $b305 === 0 ? '0|' : 'BAD|';
$b305 = '0';
echo $a305 === '0' ? 'S|' : 'BAD|';
$a305 = 1.5;
echo $b305 === 1.5 ? 'D|' : 'BAD|';
$b305 = null;
echo $a305 === null ? 'L|' : 'BAD|';
$a305 = [1];
$arraycopy305 = $box305->v;
$b305[0] = 2;
echo $arraycopy305 === [1] && $a305 === [2] && $box305->v === [2] ? 'A|' : 'BAD|';
$a305 = new \stdClass();
$objectcopy305 = $box305->v;
$objectcopy305->value = 3;
echo $b305 === $objectcopy305 && $b305->value === 3 ? 'O|' : 'BAD|';
$b305 = 37;
echo $a305 === 37 && $copy305 === false && $arraycopy305 === [1] && $objectcopy305->value === 3 ? 'K|' : 'BAD|';
unset($box305);
$a305 = 'tail';
echo $b305 === 'tail' && $copy305 === false && $arraycopy305 === [1] && $objectcopy305->value === 3 ? 'R|' : 'BAD|';
unset($a305, $b305, $copy305, $arraycopy305, $objectcopy305);
echo 'Z|';
