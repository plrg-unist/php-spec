<?php
class GC64SparePeer {}
class GC64SharedThrowPeer {
    public function __destruct() {
        global $map64Peer, $loopKey64Peer, $result64Peer, $oldWatch64Peer;
        echo 'C|', (int) ($oldWatch64Peer->get() === null), '|';
        $seen64Peer = $map64Peer[$loopKey64Peer];
        echo 'I|', (int) ($seen64Peer === null), '|',
             (int) ($result64Peer === 31), '|';
        throw new Exception('peer-child-64');
    }
}
class GC64TailPeer {
    public function __destruct() {
        global $map64Peer, $loopKey64Peer, $result64Peer, $oldWatch64Peer;
        echo 'L|', (int) ($oldWatch64Peer->get() === null), '|';
        $seen64Peer = $map64Peer[$loopKey64Peer];
        echo 'J|', (int) ($seen64Peer === null), '|',
             (int) ($result64Peer === 31), '|';
        throw new Exception('peer-later-64');
    }
}
class GC64OldPeer {
    public $lead64Peer = 17;
    public $first64Peer;
    public $last64Peer;
    public $later64Peer;
    public $tail64Peer = 23;
    public function __destruct() {
        global $map64Peer, $loopKey64Peer, $result64Peer, $oldWatch64Peer;
        echo 'O|', (int) ($oldWatch64Peer->get() === $this), '|';
        $seen64Peer = $map64Peer[$loopKey64Peer];
        echo 'U|', (int) ($seen64Peer === null), '|',
             (int) ($result64Peer === 31), '|';
        throw new Exception('peer-own-64');
    }
}
$map64Peer = new WeakMap;
$key64Peer = new stdClass;
$spareKey64Peer = new stdClass;
$old64Peer = new GC64OldPeer;
$shared64Peer = new GC64SharedThrowPeer;
$tail64Peer = new GC64TailPeer;
$old64Peer->first64Peer = $shared64Peer;
$old64Peer->last64Peer = $shared64Peer;
$old64Peer->later64Peer = $tail64Peer;
$spare64Peer = new GC64SparePeer;
$incoming64Peer = null;
$map64Peer[$spareKey64Peer] = $spare64Peer;
$map64Peer[$key64Peer] = $old64Peer;
$mapWatch64Peer = WeakReference::create($map64Peer);
$keyWatch64Peer = WeakReference::create($key64Peer);
$oldWatch64Peer = WeakReference::create($old64Peer);
$sharedWatch64Peer = WeakReference::create($shared64Peer);
$tailWatch64Peer = WeakReference::create($tail64Peer);
unset($old64Peer, $shared64Peer, $tail64Peer);
$result64Peer = 31;
$continued64Peer = 0;
echo 'B|';
try {
    foreach ($map64Peer as $loopKey64Peer => $loopValue64Peer) {
        if ($loopKey64Peer === $spareKey64Peer) {
            echo 's|', (int) ($loopValue64Peer === $spare64Peer), '|';
            continue;
        }
        $loopValue64Peer = false;
        $result64Peer = $map64Peer[$loopKey64Peer] = $incoming64Peer;
        $continued64Peer = 1;
        echo 'BAD|';
    }
} catch (Exception $error64Peer) {
    $trace64Peer = $error64Peer->getTrace();
    echo 'T|', $error64Peer->getMessage(), '|', $error64Peer->getLine(), '|',
         $trace64Peer[0]['function'], '|', $trace64Peer[0]['line'], '|',
         (int) ($result64Peer === 31), '|', $continued64Peer, '|';
    echo 'P|', $error64Peer->getPrevious()->getMessage(), '|',
         $error64Peer->getPrevious()->getLine(), '|',
         (int) ($error64Peer->getPrevious()->getPrevious() === null), '|';
    echo 'Q|', $error64Peer->getPrevious()->getPrevious()->getMessage(), '|',
         $error64Peer->getPrevious()->getPrevious()->getLine(), '|',
         (int) ($error64Peer->getPrevious()->getPrevious()->getPrevious() === null), '|';
}
echo 'R|', (int) ($result64Peer === 31), '|', $continued64Peer, '|',
     (int) ($loopValue64Peer === false), '|',
     (int) ($map64Peer[$key64Peer] === null), '|',
     (int) ($oldWatch64Peer->get() === null), '|',
     (int) ($sharedWatch64Peer->get() === null), '|',
     (int) ($tailWatch64Peer->get() === null), '|';
unset($error64Peer, $trace64Peer);
unset($map64Peer);
echo 'm|', (int) ($mapWatch64Peer->get() === null), '|';
unset($result64Peer, $incoming64Peer, $loopValue64Peer, $spare64Peer);
unset($key64Peer, $spareKey64Peer, $loopKey64Peer);
echo 'K|', (int) ($keyWatch64Peer->get() === null), '|';
