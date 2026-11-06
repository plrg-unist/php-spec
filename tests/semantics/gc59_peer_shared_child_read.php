<?php
class GC59PairPeer { public $first; public $second; }
class GC59IncomingPeer {}
class GC59ChildPeer {
    public function __destruct() {
        global $map59Peer, $loopKey59Peer, $result59Peer, $throw59Peer,
               $mapWatch59Peer, $keyWatch59Peer, $oldWatch59Peer, $incomingWatch59Peer;
        $seen59Peer = $map59Peer[$loopKey59Peer];
        echo 'C|', (int) ($oldWatch59Peer->get() === null), '|',
             (int) ($seen59Peer === $incomingWatch59Peer->get()), '|',
             (int) ($mapWatch59Peer->get() === $map59Peer), '|',
             (int) ($keyWatch59Peer->get() === $loopKey59Peer), '|',
             (int) ($result59Peer === 31), '|';
        if ($throw59Peer) { throw new Exception('peer-fresh-59'); }
    }
}
$throw59Peer = false;
$map59Peer = new WeakMap;
$key59Peer = new stdClass;
$scalarKey59Peer = new stdClass;
$old59Peer = new GC59PairPeer;
$child59Peer = new GC59ChildPeer;
$old59Peer->first = $child59Peer;
$old59Peer->second = $child59Peer;
$incoming59Peer = new GC59IncomingPeer;
$map59Peer[$scalarKey59Peer] = 17;
$map59Peer[$key59Peer] = $old59Peer;
$mapWatch59Peer = WeakReference::create($map59Peer);
$keyWatch59Peer = WeakReference::create($key59Peer);
$oldWatch59Peer = WeakReference::create($old59Peer);
$childWatch59Peer = WeakReference::create($child59Peer);
$incomingWatch59Peer = WeakReference::create($incoming59Peer);
unset($old59Peer, $child59Peer);
$result59Peer = 31;
$continued59Peer = 0;
echo 'B|';
try {
    foreach ($map59Peer as $loopKey59Peer => $loopValue59Peer) {
        if ($loopKey59Peer === $scalarKey59Peer) {
            echo 's|', $loopValue59Peer, '|';
            continue;
        }
        $loopValue59Peer = false;
        $result59Peer = $map59Peer[$loopKey59Peer] = $incoming59Peer;
        $continued59Peer = 1;
        echo 'A|', (int) ($result59Peer === $incoming59Peer), '|';
        break;
    }
} catch (Exception $error59Peer) {
    $trace59Peer = $error59Peer->getTrace();
    echo 'T|', $error59Peer->getMessage(), '|', $error59Peer->getLine(), '|',
         $trace59Peer[0]['function'], '|', $trace59Peer[0]['line'], '|',
         (int) ($result59Peer === 31), '|', $continued59Peer, '|';
}
echo 'R|', (int) ($result59Peer === 31), '|',
     (int) ($result59Peer === $incoming59Peer), '|', $continued59Peer, '|',
     (int) ($loopValue59Peer === false), '|',
     (int) ($map59Peer[$key59Peer] === $incoming59Peer), '|',
     (int) ($oldWatch59Peer->get() === null), '|',
     (int) ($childWatch59Peer->get() === null), '|';
unset($map59Peer);
echo 'M|', (int) ($mapWatch59Peer->get() === null), '|',
     (int) ($incomingWatch59Peer->get() === $incoming59Peer), '|';
unset($result59Peer, $incoming59Peer);
echo 'V|', (int) ($incomingWatch59Peer->get() === null), '|';
unset($key59Peer, $scalarKey59Peer, $loopKey59Peer);
echo 'K|', (int) ($keyWatch59Peer->get() === null), '|';
