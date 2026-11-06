<?php
class GC66LeafPeer {}
class GC66ChildPeer {
    public function __destruct() {
        global $map66Peer, $loopKey66Peer, $result66Peer, $oldWatch66Peer;
        echo 'C|', (int) ($oldWatch66Peer->get() === null), '|';
        $seenChild66Peer = $map66Peer[$loopKey66Peer];
        echo 'c|', (int) ($seenChild66Peer[0] === 17), '|',
             (int) ($result66Peer === 31), '|';
        unset($seenChild66Peer);
        echo 'd|';
    }
}
class GC66OldPeer {
    public $child66Peer = null;
    public function __destruct() {
        global $map66Peer, $loopKey66Peer, $result66Peer, $oldWatch66Peer,
               $throw66Peer;
        echo 'O|', (int) ($oldWatch66Peer->get() === $this), '|';
        $seenOwn66Peer = $map66Peer[$loopKey66Peer];
        echo 'o|', (int) ($seenOwn66Peer[0] === 17), '|',
             (int) ($result66Peer === 31), '|';
        unset($seenOwn66Peer);
        echo 'u|';
        if ($throw66Peer) { throw new Exception('peer-array-66'); }
    }
}
$throw66Peer = false;
$map66Peer = new WeakMap;
$key66Peer = new stdClass;
$otherKey66Peer = new stdClass;
$old66Peer = new GC66OldPeer;
$child66Peer = new GC66ChildPeer;
$old66Peer->child66Peer = $child66Peer;
$leaf66Peer = new GC66LeafPeer;
$shared66Peer = [$leaf66Peer, 23];
$incoming66Peer = [17, $shared66Peer, $shared66Peer, $leaf66Peer, $leaf66Peer];
$other66Peer = new GC66LeafPeer;
$map66Peer[$key66Peer] = $old66Peer;
$map66Peer[$otherKey66Peer] = $other66Peer;
$mapWatch66Peer = WeakReference::create($map66Peer);
$keyWatch66Peer = WeakReference::create($key66Peer);
$oldWatch66Peer = WeakReference::create($old66Peer);
$childWatch66Peer = WeakReference::create($child66Peer);
$leafWatch66Peer = WeakReference::create($leaf66Peer);
unset($old66Peer, $child66Peer, $shared66Peer, $leaf66Peer);
$result66Peer = 31;
$continued66Peer = 0;
echo 'B|';
try {
    foreach ($map66Peer as $loopKey66Peer => $loopValue66Peer) {
        $loopValue66Peer = false;
        $result66Peer = $map66Peer[$loopKey66Peer] = $incoming66Peer;
        $continued66Peer = 1;
        echo 'A|', (int) ($result66Peer === $incoming66Peer), '|';
        break;
    }
} catch (Exception $error66Peer) {
    $trace66Peer = $error66Peer->getTrace();
    echo 'T|', $error66Peer->getMessage(), '|', $error66Peer->getLine(), '|',
         $trace66Peer[0]['function'], '|', $trace66Peer[0]['line'], '|',
         (int) ($result66Peer === 31), '|', $continued66Peer, '|';
}
echo 'R|', (int) ($result66Peer === 31), '|',
     (int) ($result66Peer === $incoming66Peer), '|', $continued66Peer, '|',
     (int) ($map66Peer[$key66Peer] === $incoming66Peer), '|',
     (int) ($oldWatch66Peer->get() === null), '|',
     (int) ($childWatch66Peer->get() === null), '|';
unset($map66Peer);
echo 'M|', (int) ($mapWatch66Peer->get() === null), '|',
     (int) ($leafWatch66Peer->get() !== null), '|';
unset($result66Peer, $incoming66Peer);
echo 'L|', (int) ($leafWatch66Peer->get() === null), '|';
unset($loopValue66Peer, $other66Peer, $key66Peer, $otherKey66Peer, $loopKey66Peer);
echo 'K|', (int) ($keyWatch66Peer->get() === null), '|';
