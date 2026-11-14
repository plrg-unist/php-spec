<?php
namespace Ns297ArrayShortReference;
class Box297 {
    public array $items = [3] {
        &get =>
            $this->items;
    }
    public function __destruct() { echo 'D|'; }
}
$box297 = new Box297();
$alias297 =& $box297->items;
$copy297 = $box297->items;
$alias297[] = 5;
echo $alias297 === [3, 5] && $copy297 === [3] ? 'C|' : 'BAD|';
$seed297 = 11;
$alias297 = [&$seed297, [13]];
$embedded297 = $box297->items;
$alias297[1][0] = 17;
$seed297 = 19;
echo $embedded297 === [19, [13]] && $box297->items === [19, [17]] ? 'N|' : 'BAD|';
$seed297 = 'leaf';
echo $embedded297[0] === 'leaf' && $alias297[0] === 'leaf' ? 'L|' : 'BAD|';
try { $alias297 = null; } catch (\TypeError $e) { echo 'T|'; }
try { $alias297 = 23; } catch (\TypeError $e) { echo 'S|'; }
echo $alias297 === ['leaf', [17]] ? 'K|' : 'BAD|';
unset($box297);
$alias297 = 29;
echo $alias297 === 29 && $copy297 === [3] && $embedded297 === ['leaf', [13]] ? 'R|' : 'BAD|';
unset($alias297, $copy297, $embedded297, $seed297);
echo 'Z|';
