<?php
namespace Ns299NullableObjectShortReference;
class Box299 {
    public ?object $item {
        &get =>
            $this->item;
    }
    public function __destruct() { echo 'D|'; }
}
$box299 = new Box299();
echo (array)$box299 === [] ? 'U|' : 'BAD|';
$read299 = $box299->item;
echo $read299 === null && (array)$box299 === ['item' => null] ? 'V|' : 'BAD|';
unset($read299);
$alias299 =& $box299->item;
echo $alias299 === null ? 'N|' : 'BAD|';
$alias299 = new \stdClass();
$alias299->tag = 31;
$copy299 = $box299->item;
$copy299->tag = 37;
echo $alias299 === $copy299 && $box299->item === $copy299 && $alias299->tag === 37 ? 'M|' : 'BAD|';
$alias299 = null;
echo $box299->item === null && $copy299->tag === 37 ? 'Q|' : 'BAD|';
$second299 = new \stdClass();
$second299->tag = 41;
$alias299 = $second299;
echo $box299->item === $second299 && $copy299 !== $second299 ? 'C|' : 'BAD|';
try { $alias299 = 43; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns299NullableObjectShortReference\Box299::$item of type ?object' ? 'T|' : 'BAD|';
}
unset($e);
echo $alias299 === $second299 ? 'K|' : 'BAD|';
unset($box299);
$alias299 = [];
echo $alias299 === [] && $copy299->tag === 37 && $second299->tag === 41 ? 'R|' : 'BAD|';
unset($alias299, $copy299, $second299);
echo 'Z|';
