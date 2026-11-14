<?php
namespace Ns298NullArrayShortReference;
class Box298 {
    public null|array $items = [83] {
        &get =>
            $this->items;
    }
    public function __destruct() { echo 'D|'; }
}
$box298 = new Box298();
$alias298 =& $box298->items;
$copy298 = $box298->items;
$alias298[] = 89;
echo $alias298 === [83, 89] && $copy298 === [83] ? 'C|' : 'BAD|';
$alias298 = null;
echo $box298->items === null ? 'N|' : 'BAD|';
$alias298 = [[97]];
$nested298 = $box298->items;
$alias298[0][0] = 101;
echo $alias298 === [[101]] && $nested298 === [[97]] ? 'M|' : 'BAD|';
try { $alias298 = 103; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns298NullArrayShortReference\Box298::$items of type ?array' ? 'T|' : 'BAD|';
}
unset($e);
echo $alias298 === [[101]] ? 'K|' : 'BAD|';
unset($box298);
$alias298 = 'released';
echo $alias298 === 'released' && $copy298 === [83] && $nested298 === [[97]] ? 'R|' : 'BAD|';
unset($alias298, $copy298, $nested298);
echo 'Z|';
