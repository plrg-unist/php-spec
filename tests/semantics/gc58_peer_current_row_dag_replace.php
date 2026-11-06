<?php
class ReplacePayload58Peer { public $child; }
class ReplaceOldChild58Peer {
    public function __destruct() {
        global $mapWatch58Peer, $keyWatch58Peer, $newChildWatch58Peer;
        echo 'O|', (int) ($mapWatch58Peer->get() === NULL), '|',
            (int) ($keyWatch58Peer->get() === NULL), '|',
            (int) ($newChildWatch58Peer->get() === NULL), '|';
    }
}
class ReplaceNewChild58Peer {
    public function __destruct() {
        global $mapWatch58Peer, $keyWatch58Peer, $oldChildWatch58Peer, $newValueWatch58Peer;
        echo 'N|', (int) ($mapWatch58Peer->get() !== NULL), '|',
            (int) ($keyWatch58Peer->get() !== NULL), '|',
            (int) ($oldChildWatch58Peer->get() !== NULL), '|',
            (int) ($newValueWatch58Peer->get() === NULL), '|';
    }
}
$arrayKey58Peer = new stdClass();
$scalarKey58Peer = new stdClass();
$map58Peer = new WeakMap();
$oldValue58Peer = new ReplacePayload58Peer();
$oldChild58Peer = new ReplaceOldChild58Peer();
$oldValue58Peer->child = $oldChild58Peer;
$newValue58Peer = new ReplacePayload58Peer();
$newChild58Peer = new ReplaceNewChild58Peer();
$newValue58Peer->child = $newChild58Peer;
$mapWatch58Peer = WeakReference::create($map58Peer);
$keyWatch58Peer = WeakReference::create($arrayKey58Peer);
$oldChildWatch58Peer = WeakReference::create($oldChild58Peer);
$newChildWatch58Peer = WeakReference::create($newChild58Peer);
$newValueWatch58Peer = WeakReference::create($newValue58Peer);
$oldInner58Peer = [$oldValue58Peer, 0, $oldValue58Peer];
$oldOuter58Peer = [$oldInner58Peer, $oldInner58Peer];
$map58Peer[$scalarKey58Peer] = 17;
$map58Peer[$arrayKey58Peer] = $oldOuter58Peer;
unset($oldValue58Peer, $oldChild58Peer, $newChild58Peer, $oldInner58Peer);
echo 'B|';
foreach ($map58Peer as $loopKey58Peer => $loopValue58Peer) {
    if ($loopKey58Peer === $scalarKey58Peer) {
        $assigned58Peer = ($map58Peer[$loopKey58Peer] = 23);
        echo 's|', $loopValue58Peer, '|', $assigned58Peer, '|',
            $map58Peer[$loopKey58Peer], '|';
        continue;
    }
    $assigned58Peer = ($map58Peer[$loopKey58Peer] = $newValue58Peer);
    echo 'W|', (int) ($loopValue58Peer === $oldOuter58Peer), '|',
        (int) ($assigned58Peer === $newValue58Peer), '|',
        (int) ($map58Peer[$loopKey58Peer] === $newValue58Peer), '|';
    unset($oldOuter58Peer, $assigned58Peer, $newValue58Peer, $map58Peer);
    echo 'P|', (int) ($mapWatch58Peer->get() !== NULL), '|',
        (int) ($oldChildWatch58Peer->get() !== NULL), '|';
    break;
}
echo 'D|', (int) ($mapWatch58Peer->get() === NULL), '|',
    (int) ($oldChildWatch58Peer->get() !== NULL), '|',
    (int) ($newChildWatch58Peer->get() === NULL), '|';
unset($arrayKey58Peer, $scalarKey58Peer);
echo 'K|', (int) ($keyWatch58Peer->get() === $loopKey58Peer), '|';
unset($loopKey58Peer);
echo 'k|', (int) ($keyWatch58Peer->get() === NULL), '|';
unset($loopValue58Peer);
echo 'F|', (int) ($oldChildWatch58Peer->get() === NULL), '|';
