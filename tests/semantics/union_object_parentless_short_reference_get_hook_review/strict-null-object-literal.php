<?php
declare(strict_types=1);
class OrderedObject300PeerLeaf { public int $mark = 31; }
class OrderedObject300PeerBox {
    public null|object $slot = null {
        &get =>
            $this->{'slot'};
    }
}
$box300peer = new OrderedObject300PeerBox();
$box300peer->slot = new OrderedObject300PeerLeaf();
$ref300peer =& $box300peer->slot;
$copy300peer = $ref300peer;
$alias300peer =& $ref300peer;
$alias300peer->mark = 47;
echo $copy300peer === $box300peer->slot ? "I|" : "?|";
echo $copy300peer->mark;
echo "|";
$alias300peer = null;
echo $ref300peer === null ? "N|" : "?|";
echo $copy300peer->mark;
echo "|";
$keep300peer = $box300peer;
unset($box300peer);
try { $ref300peer = 83; }
catch (TypeError $error300peer) { echo $error300peer->getMessage(); echo "|"; }
$alias300peer = new OrderedObject300PeerLeaf();
echo $alias300peer === $copy300peer ? "?|" : "R|";
unset($keep300peer);
$ref300peer = 89;
echo $alias300peer;
echo "|";
unset($ref300peer, $alias300peer, $copy300peer);
echo "E|";
