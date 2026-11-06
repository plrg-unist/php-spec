<?php
class ReadPayload57Peer { public $child; }
class ReadChild57Peer {
    public function __destruct() {
        global $mapWatch57Peer, $keyWatch57Peer, $valueWatch57Peer;
        echo 'C|', (int) ($mapWatch57Peer->get() === NULL), '|',
            (int) ($keyWatch57Peer->get() === NULL), '|',
            (int) ($valueWatch57Peer->get() === NULL), '|';
    }
}
$arrayKey57Peer = new stdClass();
$scalarKey57Peer = new stdClass();
$map57Peer = new WeakMap();
$value57Peer = new ReadPayload57Peer();
$child57Peer = new ReadChild57Peer();
$value57Peer->child = $child57Peer;
$mapWatch57Peer = WeakReference::create($map57Peer);
$keyWatch57Peer = WeakReference::create($arrayKey57Peer);
$valueWatch57Peer = WeakReference::create($value57Peer);
$childWatch57Peer = WeakReference::create($child57Peer);
$inner57Peer = [$value57Peer, 0, $value57Peer];
$outer57Peer = [$inner57Peer, $inner57Peer];
$map57Peer[$scalarKey57Peer] = 17;
$map57Peer[$arrayKey57Peer] = $outer57Peer;
unset($value57Peer, $child57Peer, $inner57Peer, $outer57Peer);
echo 'B|';
foreach ($map57Peer as $loopKey57Peer => $loopValue57Peer) {
    $held57Peer = $map57Peer[$loopKey57Peer];
    if ($loopKey57Peer === $scalarKey57Peer) {
        echo 's|', $held57Peer, '|';
        continue;
    }
    echo 'R|', (int) ($held57Peer[0][0] === $loopValue57Peer[1][2]), '|';
    unset($loopValue57Peer, $map57Peer);
    echo 'L|', (int) ($mapWatch57Peer->get() !== NULL), '|',
        (int) ($childWatch57Peer->get() !== NULL), '|';
    break;
}
echo 'D|', (int) ($mapWatch57Peer->get() === NULL), '|',
    (int) ($childWatch57Peer->get() !== NULL), '|', $held57Peer[0][1], '|';
unset($arrayKey57Peer, $scalarKey57Peer);
echo 'K|', (int) ($keyWatch57Peer->get() === $loopKey57Peer), '|';
unset($loopKey57Peer);
echo 'k|', (int) ($keyWatch57Peer->get() === NULL), '|';
unset($held57Peer);
echo 'F|', (int) ($childWatch57Peer->get() === NULL), '|';
