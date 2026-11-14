<?php
declare(strict_types=1);
namespace Ns299ObjectShortReferencePeer;
class Box299 {
    public object $item {
        &get =>
            $this->{'item'};
    }
    public function __destruct() { echo 'D|'; }
}
class Leaf299 { public $value = 23; }
$box299peer = new Box299();
$seed299peer = new \stdClass();
$seed299peer->value = 11;
$box299peer->item = $seed299peer;
unset($seed299peer);
$alias299peer =& $box299peer->item;
$copy299peer = $box299peer->item;
echo $alias299peer === $copy299peer ? 'I|' : 'BAD|';
$copy299peer->value = 17;
echo $alias299peer->value === 17 ? 'M|' : 'BAD|';
$alias299peer = new Leaf299();
echo $alias299peer !== $copy299peer && $alias299peer->value === 23 && $copy299peer->value === 17 ? 'S|' : 'BAD|';
try { $alias299peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns299ObjectShortReferencePeer\\Box299::$item of type object' ? 'N|' : 'BAD|';
}
try { $alias299peer = 29; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns299ObjectShortReferencePeer\\Box299::$item of type object' ? 'T|' : 'BAD|';
}
unset($e);
echo $alias299peer->value === 23 && $copy299peer->value === 17 ? 'K|' : 'BAD|';
unset($box299peer);
$alias299peer = false;
echo $alias299peer === false && $copy299peer->value === 17 ? 'R|' : 'BAD|';
unset($alias299peer, $copy299peer);
echo 'Z|';
