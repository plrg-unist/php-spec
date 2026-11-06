<?php
class GC67LeafPeer {}
class GC67MiddlePeer {
    public function __destruct() {
        global $map67Peer, $loopKey67Peer, $result67Peer, $oldWatch67Peer;
        $seen67Peer = $map67Peer[$loopKey67Peer];
        echo 'M|', (int) ($oldWatch67Peer->get() === null), '|',
             (int) ($seen67Peer === null), '|', (int) ($result67Peer === 31), '|';
    }
}
class GC67ArrayChildPeer {
    public function __destruct() {
        global $map67Peer, $loopKey67Peer, $result67Peer, $oldWatch67Peer,
               $throwArray67Peer;
        $seen67Peer = $map67Peer[$loopKey67Peer];
        echo 'A|', (int) ($oldWatch67Peer->get() === null), '|',
             (int) ($seen67Peer === null), '|', (int) ($result67Peer === 31), '|';
        if ($throwArray67Peer) { throw new Exception('peer-array-child-67'); }
    }
}
class GC67TailPeer {
    public function __destruct() {
        global $map67Peer, $loopKey67Peer, $result67Peer, $oldWatch67Peer;
        $seen67Peer = $map67Peer[$loopKey67Peer];
        echo 'L|', (int) ($oldWatch67Peer->get() === null), '|',
             (int) ($seen67Peer === null), '|', (int) ($result67Peer === 31), '|';
    }
}
class GC67OldPeer {
    public $firstBox67Peer = null;
    public $middle67Peer = null;
    public $lastBox67Peer = null;
    public $tail67Peer = null;
    public function __destruct() {
        global $map67Peer, $loopKey67Peer, $result67Peer, $oldWatch67Peer,
               $throwOwn67Peer;
        echo 'O|', (int) ($oldWatch67Peer->get() === $this), '|';
        $seen67Peer = $map67Peer[$loopKey67Peer];
        echo 'U|', (int) ($seen67Peer === null), '|', (int) ($result67Peer === 31), '|';
        if ($throwOwn67Peer) { throw new Exception('peer-own-67'); }
    }
}
$throwOwn67Peer = false;
$throwArray67Peer = false;
$map67Peer = new WeakMap;
$key67Peer = new stdClass;
$otherKey67Peer = new stdClass;
$old67Peer = new GC67OldPeer;
$middle67Peer = new GC67MiddlePeer;
$sharedChild67Peer = new GC67ArrayChildPeer;
$tail67Peer = new GC67TailPeer;
$box67Peer = [17, $sharedChild67Peer, $sharedChild67Peer, 23];
$old67Peer->firstBox67Peer = $box67Peer;
$old67Peer->middle67Peer = $middle67Peer;
$old67Peer->lastBox67Peer = $box67Peer;
$old67Peer->tail67Peer = $tail67Peer;
$other67Peer = new GC67LeafPeer;
$incoming67Peer = null;
$map67Peer[$key67Peer] = $old67Peer;
$map67Peer[$otherKey67Peer] = $other67Peer;
$mapWatch67Peer = WeakReference::create($map67Peer);
$keyWatch67Peer = WeakReference::create($key67Peer);
$oldWatch67Peer = WeakReference::create($old67Peer);
$middleWatch67Peer = WeakReference::create($middle67Peer);
$sharedWatch67Peer = WeakReference::create($sharedChild67Peer);
$tailWatch67Peer = WeakReference::create($tail67Peer);
unset($old67Peer, $middle67Peer, $sharedChild67Peer, $tail67Peer, $box67Peer);
$result67Peer = 31;
$continued67Peer = 0;
echo 'B|';
try {
    foreach ($map67Peer as $loopKey67Peer => $loopValue67Peer) {
        $loopValue67Peer = false;
        $result67Peer = $map67Peer[$loopKey67Peer] = $incoming67Peer;
        $continued67Peer = 1;
        echo 'N|', (int) ($result67Peer === $incoming67Peer), '|';
        break;
    }
} catch (Exception $error67Peer) {
    $trace67Peer = $error67Peer->getTrace();
    echo 'E|', $error67Peer->getMessage(), '|', $error67Peer->getLine(), '|',
         $trace67Peer[0]['function'], '|', $trace67Peer[0]['line'], '|',
         (int) ($result67Peer === 31), '|', $continued67Peer, '|';
    if ($throwArray67Peer) {
        $previous67Peer = $error67Peer->getPrevious();
        echo 'P|', $previous67Peer->getMessage(), '|',
             (int) ($previous67Peer->getPrevious() === null), '|';
    }
}
echo 'R|', (int) ($result67Peer === 31), '|',
     (int) ($result67Peer === $incoming67Peer), '|', $continued67Peer, '|',
     (int) ($map67Peer[$key67Peer] === null), '|',
     (int) ($oldWatch67Peer->get() === null), '|',
     (int) ($middleWatch67Peer->get() === null), '|',
     (int) ($sharedWatch67Peer->get() === null), '|',
     (int) ($tailWatch67Peer->get() === null), '|';
unset($map67Peer);
echo 'm|', (int) ($mapWatch67Peer->get() === null), '|';
unset($result67Peer, $incoming67Peer, $loopValue67Peer, $other67Peer);
unset($key67Peer, $otherKey67Peer, $loopKey67Peer);
echo 'K|', (int) ($keyWatch67Peer->get() === null), '|';
