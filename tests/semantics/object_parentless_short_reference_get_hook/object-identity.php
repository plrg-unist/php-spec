<?php
namespace Ns299ObjectShortReference;
class Box299 {
    public object $item {
        &get =>
            $this->item;
    }
    public function __destruct() { echo 'D|'; }
}
$first299 = new \stdClass();
$first299->tag = 17;
$box299 = new Box299();
$box299->item = $first299;
$alias299 =& $box299->item;
$copy299 = $box299->item;
echo $alias299 === $first299 && $copy299 === $first299 ? 'G|' : 'BAD|';
$copy299->tag = 19;
echo $alias299->tag === 19 && $box299->item === $copy299 ? 'M|' : 'BAD|';
$second299 = new \stdClass();
$second299->tag = 23;
$alias299 = $second299;
echo $box299->item === $second299 && $copy299 === $first299 && $copy299->tag === 19 ? 'C|' : 'BAD|';
try { $alias299 = null; } catch (\TypeError $e) { echo 'T|'; }
try { $alias299 = 29; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns299ObjectShortReference\Box299::$item of type object' ? 'S|' : 'BAD|';
}
unset($e);
echo $alias299 === $second299 ? 'K|' : 'BAD|';
unset($box299);
$alias299 = 'released';
echo $alias299 === 'released' && $copy299->tag === 19 && $second299->tag === 23 ? 'R|' : 'BAD|';
unset($alias299, $first299, $second299, $copy299);
echo 'Z|';
