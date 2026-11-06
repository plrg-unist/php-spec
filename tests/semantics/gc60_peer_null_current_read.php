<?php
class GC60PairPeer { public $first; public $second; }
class GC60ChildPeer {
    public function __destruct() {
        global $map60Peer, $loopKey60Peer, $result60Peer, $throw60Peer,
               $mapWatch60Peer, $keyWatch60Peer, $oldWatch60Peer;
        $seen60Peer = $map60Peer[$loopKey60Peer];
        echo 'C|', (int) ($oldWatch60Peer->get() === null), '|',
             (int) ($seen60Peer === null), '|',
             (int) ($mapWatch60Peer->get() === $map60Peer), '|',
             (int) ($keyWatch60Peer->get() === $loopKey60Peer), '|',
             (int) ($result60Peer === 31), '|';
        if ($throw60Peer) { throw new Exception('peer-fresh-60'); }
    }
}
$throw60Peer = false;
$map60Peer = new WeakMap;
$key60Peer = new stdClass;
$scalarKey60Peer = new stdClass;
$old60Peer = new GC60PairPeer;
$child60Peer = new GC60ChildPeer;
$old60Peer->first = $child60Peer;
$old60Peer->second = $child60Peer;
$incoming60Peer = null;
$map60Peer[$scalarKey60Peer] = 17;
$map60Peer[$key60Peer] = $old60Peer;
$mapWatch60Peer = WeakReference::create($map60Peer);
$keyWatch60Peer = WeakReference::create($key60Peer);
$oldWatch60Peer = WeakReference::create($old60Peer);
$childWatch60Peer = WeakReference::create($child60Peer);
unset($old60Peer, $child60Peer);
$result60Peer = 31;
$continued60Peer = 0;
echo 'B|';
try {
    foreach ($map60Peer as $loopKey60Peer => $loopValue60Peer) {
        if ($loopKey60Peer === $scalarKey60Peer) {
            echo 's|', $loopValue60Peer, '|';
            continue;
        }
        $loopValue60Peer = false;
        $result60Peer = $map60Peer[$loopKey60Peer] = $incoming60Peer;
        $continued60Peer = 1;
        echo 'A|', (int) ($result60Peer === $incoming60Peer), '|';
        break;
    }
} catch (Exception $error60Peer) {
    $trace60Peer = $error60Peer->getTrace();
    echo 'T|', $error60Peer->getMessage(), '|', $error60Peer->getLine(), '|',
         $trace60Peer[0]['function'], '|', $trace60Peer[0]['line'], '|',
         (int) ($result60Peer === 31), '|', $continued60Peer, '|';
}
echo 'R|', (int) ($result60Peer === 31), '|',
     (int) ($result60Peer === $incoming60Peer), '|', $continued60Peer, '|',
     (int) ($loopValue60Peer === false), '|',
     (int) ($map60Peer[$key60Peer] === $incoming60Peer), '|',
     (int) ($oldWatch60Peer->get() === null), '|',
     (int) ($childWatch60Peer->get() === null), '|';
unset($map60Peer);
echo 'M|', (int) ($mapWatch60Peer->get() === null), '|',
     (int) ($incoming60Peer === null), '|';
unset($result60Peer, $incoming60Peer);
unset($key60Peer, $scalarKey60Peer, $loopKey60Peer);
echo 'K|', (int) ($keyWatch60Peer->get() === null), '|';
