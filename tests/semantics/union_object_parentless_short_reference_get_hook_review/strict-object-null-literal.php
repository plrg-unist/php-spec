<?php
declare(strict_types=1);
class OrderedObject300PeerLeaf { public int $mark = 31; }
class OrderedObject300PeerBox {
    public object|null $slot {
        &get =>
            $this->{"sl\x6ft"};
    }
}
$box300peer = new OrderedObject300PeerBox();
$ref300peer =& $box300peer->slot;
echo $ref300peer === null ? "N|" : "?|";
$ref300peer = new OrderedObject300PeerLeaf();
$copy300peer = $ref300peer;
$alias300peer =& $ref300peer;
$alias300peer->mark = 43;
echo $copy300peer === $box300peer->slot ? "I|" : "?|";
echo $copy300peer->mark;
echo "|";
$alias300peer = null;
echo $ref300peer === null ? "Z|" : "?|";
echo $copy300peer->mark;
echo "|";
try { $ref300peer = 77; }
catch (TypeError $error300peer) { echo $error300peer->getMessage(); echo "|"; }
$alias300peer = new OrderedObject300PeerLeaf();
echo $alias300peer === $copy300peer ? "?|" : "R|";
unset($box300peer);
$alias300peer = 79;
echo $ref300peer;
echo "|";
unset($ref300peer, $alias300peer, $copy300peer);
echo "E|";
