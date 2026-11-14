<?php
declare(strict_types=1);
namespace Ns299NullableObjectShortReferencePeer;
class Box299 {
    public ?object $item {
        &get =>
            $this->{'item'};
    }
    public function __destruct() { echo 'D|'; }
}
class Leaf299 { public $value = 43; }
$box299peer = new Box299();
echo (array)$box299peer === [] ? 'U|' : 'BAD|';
$read299peer = $box299peer->item;
echo $read299peer === null && (array)$box299peer === ['item' => null] ? 'V|' : 'BAD|';
unset($read299peer);
$alias299peer =& $box299peer->item;
$seed299peer = new \stdClass();
$seed299peer->value = 31;
$alias299peer = $seed299peer;
unset($seed299peer);
$copy299peer = $box299peer->item;
echo $alias299peer === $copy299peer ? 'I|' : 'BAD|';
$copy299peer->value = 37;
echo $alias299peer->value === 37 ? 'M|' : 'BAD|';
$alias299peer = null;
echo $box299peer->item === null && $copy299peer->value === 37 ? 'Q|' : 'BAD|';
try { $alias299peer = 41; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns299NullableObjectShortReferencePeer\\Box299::$item of type ?object' ? 'T|' : 'BAD|';
}
unset($e);
echo $alias299peer === null ? 'K|' : 'BAD|';
$alias299peer = new Leaf299();
echo $alias299peer !== $copy299peer && $alias299peer->value === 43 && $copy299peer->value === 37 ? 'A|' : 'BAD|';
unset($box299peer);
$alias299peer = 'released';
echo $alias299peer === 'released' && $copy299peer->value === 37 ? 'R|' : 'BAD|';
unset($alias299peer, $copy299peer);
echo 'Z|';
