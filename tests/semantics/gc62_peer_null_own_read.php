<?php
class GC62SparePeer {}
class GC62OldPeer {
    public function __destruct() {
        global $map62Peer, $loopKey62Peer, $result62Peer, $throw62Peer,
               $mapWatch62Peer, $keyWatch62Peer, $oldWatch62Peer;
        echo 'L|', (int) ($oldWatch62Peer->get() === $this), '|';
        $seen62Peer = $map62Peer[$loopKey62Peer];
        echo 'C|', (int) ($seen62Peer === null), '|',
             (int) ($mapWatch62Peer->get() === $map62Peer), '|',
             (int) ($keyWatch62Peer->get() === $loopKey62Peer), '|',
             (int) ($result62Peer === 31), '|';
        if ($throw62Peer) { throw new Exception('peer-fresh-62'); }
    }
}
$throw62Peer = false;
$map62Peer = new WeakMap;
$key62Peer = new stdClass;
$spareKey62Peer = new stdClass;
$old62Peer = new GC62OldPeer;
$spare62Peer = new GC62SparePeer;
$incoming62Peer = null;
$map62Peer[$spareKey62Peer] = $spare62Peer;
$map62Peer[$key62Peer] = $old62Peer;
$mapWatch62Peer = WeakReference::create($map62Peer);
$keyWatch62Peer = WeakReference::create($key62Peer);
$oldWatch62Peer = WeakReference::create($old62Peer);
unset($old62Peer);
$result62Peer = 31;
$continued62Peer = 0;
echo 'B|';
try {
    foreach ($map62Peer as $loopKey62Peer => $loopValue62Peer) {
        if ($loopKey62Peer === $spareKey62Peer) {
            echo 's|', (int) ($loopValue62Peer === $spare62Peer), '|';
            continue;
        }
        $loopValue62Peer = false;
        $result62Peer = $map62Peer[$loopKey62Peer] = $incoming62Peer;
        $continued62Peer = 1;
        echo 'A|', (int) ($result62Peer === $incoming62Peer), '|';
        break;
    }
} catch (Exception $error62Peer) {
    $trace62Peer = $error62Peer->getTrace();
    echo 'T|', $error62Peer->getMessage(), '|', $error62Peer->getLine(), '|',
         $trace62Peer[0]['function'], '|', $trace62Peer[0]['line'], '|',
         (int) ($result62Peer === 31), '|', $continued62Peer, '|';
}
echo 'R|', (int) ($result62Peer === 31), '|',
     (int) ($result62Peer === $incoming62Peer), '|', $continued62Peer, '|',
     (int) ($loopValue62Peer === false), '|',
     (int) ($map62Peer[$key62Peer] === $incoming62Peer), '|',
     (int) ($oldWatch62Peer->get() === null), '|';
unset($map62Peer);
echo 'M|', (int) ($mapWatch62Peer->get() === null), '|',
     (int) ($incoming62Peer === null), '|';
unset($result62Peer, $incoming62Peer, $loopValue62Peer, $spare62Peer);
unset($key62Peer, $spareKey62Peer, $loopKey62Peer);
echo 'K|', (int) ($keyWatch62Peer->get() === null), '|';
