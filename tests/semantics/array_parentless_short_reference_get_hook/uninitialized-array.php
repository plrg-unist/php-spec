<?php
namespace Ns297UninitializedArrayShortReference;
class Box297 {
    public array $items {
        &get =>
            $this->items;
    }
    public function __destruct() { echo 'D|'; }
}
$box297 = new Box297();
$probe297 = [41];
$shadow297 =& $probe297;
echo (array)$box297 === [] ? 'U|' : 'BAD|';
try { $read297 = $box297->items; } catch (\Error $e) { echo 'V|'; }
try { $probe297 =& $box297->items; } catch (\Error $e) { echo 'E|'; }
echo $probe297 === [41] && $shadow297 === [41] && (array)$box297 === [] ? 'K|' : 'BAD|';
$probe297[] = 43;
echo $shadow297 === [41, 43] ? 'A|' : 'BAD|';
$box297->items = [47];
$alias297 =& $box297->items;
$copy297 = $box297->items;
$alias297[] = 53;
echo $box297->items === [47, 53] && $copy297 === [47] ? 'C|' : 'BAD|';
unset($box297);
$alias297 = null;
echo $alias297 === null && $copy297 === [47] ? 'R|' : 'BAD|';
unset($alias297, $copy297, $probe297, $shadow297);
echo 'Z|';
