<?php
class GC63SparePeer {}
class GC63MiddlePeer {
    public function __destruct() {
        global $map63Peer, $loopKey63Peer, $result63Peer, $oldWatch63Peer;
        echo 'M|', (int) ($oldWatch63Peer->get() === null), '|';
        $seen63Peer = $map63Peer[$loopKey63Peer];
        echo 'I|', (int) ($seen63Peer === null), '|',
             (int) ($result63Peer === 31), '|';
    }
}
class GC63SharedPeer {
    public function __destruct() {
        global $map63Peer, $loopKey63Peer, $result63Peer, $oldWatch63Peer;
        echo 'C|', (int) ($oldWatch63Peer->get() === null), '|';
        $seen63Peer = $map63Peer[$loopKey63Peer];
        echo 'J|', (int) ($seen63Peer === null), '|',
             (int) ($result63Peer === 31), '|';
    }
}
class GC63OldPeer {
    public $lead63Peer = 17;
    public $first63Peer;
    public $middle63Peer;
    public $last63Peer;
    public $tail63Peer = 23;
    public function __destruct() {
        global $map63Peer, $loopKey63Peer, $result63Peer, $throw63Peer,
               $mapWatch63Peer, $keyWatch63Peer, $oldWatch63Peer;
        echo 'O|', (int) ($oldWatch63Peer->get() === $this), '|';
        $seen63Peer = $map63Peer[$loopKey63Peer];
        echo 'U|', (int) ($seen63Peer === null), '|',
             (int) ($mapWatch63Peer->get() === $map63Peer), '|',
             (int) ($keyWatch63Peer->get() === $loopKey63Peer), '|',
             (int) ($result63Peer === 31), '|';
        if ($throw63Peer) { throw new Exception('peer-fresh-63'); }
        echo 'o|';
    }
}
$throw63Peer = false;
$map63Peer = new WeakMap;
$key63Peer = new stdClass;
$spareKey63Peer = new stdClass;
$old63Peer = new GC63OldPeer;
$shared63Peer = new GC63SharedPeer;
$middle63Peer = new GC63MiddlePeer;
$old63Peer->first63Peer = $shared63Peer;
$old63Peer->middle63Peer = $middle63Peer;
$old63Peer->last63Peer = $shared63Peer;
$spare63Peer = new GC63SparePeer;
$incoming63Peer = null;
$map63Peer[$spareKey63Peer] = $spare63Peer;
$map63Peer[$key63Peer] = $old63Peer;
$mapWatch63Peer = WeakReference::create($map63Peer);
$keyWatch63Peer = WeakReference::create($key63Peer);
$oldWatch63Peer = WeakReference::create($old63Peer);
$sharedWatch63Peer = WeakReference::create($shared63Peer);
$middleWatch63Peer = WeakReference::create($middle63Peer);
unset($old63Peer, $shared63Peer, $middle63Peer);
$result63Peer = 31;
$continued63Peer = 0;
echo 'B|';
try {
    foreach ($map63Peer as $loopKey63Peer => $loopValue63Peer) {
        if ($loopKey63Peer === $spareKey63Peer) {
            echo 's|', (int) ($loopValue63Peer === $spare63Peer), '|';
            continue;
        }
        $loopValue63Peer = false;
        $result63Peer = $map63Peer[$loopKey63Peer] = $incoming63Peer;
        $continued63Peer = 1;
        echo 'A|', (int) ($result63Peer === $incoming63Peer), '|';
        break;
    }
} catch (Exception $error63Peer) {
    $trace63Peer = $error63Peer->getTrace();
    echo 'T|', $error63Peer->getMessage(), '|', $error63Peer->getLine(), '|',
         $trace63Peer[0]['function'], '|', $trace63Peer[0]['line'], '|',
         (int) ($result63Peer === 31), '|', $continued63Peer, '|';
}
echo 'R|', (int) ($result63Peer === 31), '|',
     (int) ($result63Peer === $incoming63Peer), '|', $continued63Peer, '|',
     (int) ($loopValue63Peer === false), '|',
     (int) ($map63Peer[$key63Peer] === $incoming63Peer), '|',
     (int) ($oldWatch63Peer->get() === null), '|',
     (int) ($sharedWatch63Peer->get() === null), '|',
     (int) ($middleWatch63Peer->get() === null), '|';
unset($map63Peer);
echo 'm|', (int) ($mapWatch63Peer->get() === null), '|',
     (int) ($incoming63Peer === null), '|';
unset($result63Peer, $incoming63Peer, $loopValue63Peer, $spare63Peer);
unset($key63Peer, $spareKey63Peer, $loopKey63Peer);
echo 'K|', (int) ($keyWatch63Peer->get() === null), '|';
