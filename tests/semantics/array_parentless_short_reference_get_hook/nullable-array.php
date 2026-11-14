<?php
namespace Ns297NullableArrayShortReference;
class Box297 {
    public ?array $items = null {
        &get =>
            $this->items;
    }
    public function __destruct() { echo 'D|'; }
}
$box297 = new Box297();
echo (array)$box297 === ['items' => null] ? 'I|' : 'BAD|';
$alias297 =& $box297->items;
echo $alias297 === null ? 'N|' : 'BAD|';
$alias297 = [[31]];
$copy297 = $box297->items;
$alias297[0][0] = 37;
echo $box297->items === [[37]] && $copy297 === [[31]] ? 'C|' : 'BAD|';
$alias297 = null;
echo $box297->items === null && $copy297 === [[31]] ? 'Q|' : 'BAD|';
try { $alias297 = false; } catch (\TypeError $e) { echo 'T|'; }
echo $alias297 === null ? 'K|' : 'BAD|';
unset($box297);
$alias297 = 'released';
echo $alias297 === 'released' && $copy297 === [[31]] ? 'R|' : 'BAD|';
unset($alias297, $copy297);
echo 'Z|';
