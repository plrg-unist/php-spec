<?php
namespace Ns298ArrayNullShortReference;
class Box298 {
    public array|null $items {
        &get =>
            $this->items;
    }
    public function __destruct() { echo 'D|'; }
}
$box298 = new Box298();
echo (array)$box298 === [] ? 'U|' : 'BAD|';
$read298 = $box298->items;
echo $read298 === null && (array)$box298 === ['items' => null] ? 'V|' : 'BAD|';
unset($read298);
$alias298 =& $box298->items;
echo $alias298 === null ? 'N|' : 'BAD|';
$seed298 = 61;
$alias298 = [&$seed298, [67]];
$copy298 = $box298->items;
$alias298[1][0] = 71;
$seed298 = 'leaf';
echo $copy298 === ['leaf', [67]] && $alias298 === ['leaf', [71]] ? 'C|' : 'BAD|';
try { $alias298 = 73; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns298ArrayNullShortReference\Box298::$items of type ?array' ? 'T|' : 'BAD|';
}
unset($e);
echo $alias298 === ['leaf', [71]] ? 'K|' : 'BAD|';
$alias298 = null;
echo $box298->items === null && $copy298 === ['leaf', [67]] ? 'Q|' : 'BAD|';
unset($box298);
$alias298 = 79;
echo $alias298 === 79 && $copy298 === ['leaf', [67]] ? 'R|' : 'BAD|';
unset($alias298, $copy298, $seed298);
echo 'Z|';
