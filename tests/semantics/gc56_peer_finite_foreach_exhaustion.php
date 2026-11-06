<?php
class ForeachPayload56Peer {
    public $tag;
    public $child;
}
class ForeachFirstChild56Peer {
    public function __destruct() {
        global $mapWatch56Peer, $firstWatch56Peer, $lastWatch56Peer, $firstKeyWatch56Peer;
        echo 'A|', (int) ($mapWatch56Peer->get() !== NULL), '|',
            (int) ($firstWatch56Peer->get() === NULL), '|',
            (int) ($lastWatch56Peer->get() !== NULL), '|',
            (int) ($firstKeyWatch56Peer->get() !== NULL), '|';
    }
}
class ForeachLastChild56Peer {
    public function __destruct() {
        global $mapWatch56Peer, $lastWatch56Peer, $lastKeyWatch56Peer, $firstChildWatch56Peer;
        echo 'Z|', (int) ($mapWatch56Peer->get() === NULL), '|',
            (int) ($lastWatch56Peer->get() === NULL), '|',
            (int) ($lastKeyWatch56Peer->get() === NULL), '|',
            (int) ($firstChildWatch56Peer->get() === NULL), '|';
    }
}
$lastKey56Peer = new stdClass();
$firstKey56Peer = new stdClass();
$scalarKey56Peer = new stdClass();
$map56Peer = new WeakMap();
$mapWatch56Peer = WeakReference::create($map56Peer);
$firstKeyWatch56Peer = WeakReference::create($firstKey56Peer);
$lastKeyWatch56Peer = WeakReference::create($lastKey56Peer);
$firstChild56Peer = new ForeachFirstChild56Peer();
$lastChild56Peer = new ForeachLastChild56Peer();
$firstChildWatch56Peer = WeakReference::create($firstChild56Peer);
$lastChildWatch56Peer = WeakReference::create($lastChild56Peer);
$first56Peer = new ForeachPayload56Peer();
$first56Peer->tag = 23;
$first56Peer->child = $firstChild56Peer;
$last56Peer = new ForeachPayload56Peer();
$last56Peer->tag = 41;
$last56Peer->child = $lastChild56Peer;
$firstWatch56Peer = WeakReference::create($first56Peer);
$lastWatch56Peer = WeakReference::create($last56Peer);
$inner56Peer = [$last56Peer, 9, $last56Peer];
$outer56Peer = [$inner56Peer, $inner56Peer];
$map56Peer[$scalarKey56Peer] = 17;
$map56Peer[$firstKey56Peer] = $first56Peer;
$map56Peer[$lastKey56Peer] = $outer56Peer;
unset($firstChild56Peer, $lastChild56Peer, $first56Peer, $last56Peer, $inner56Peer, $outer56Peer);
echo 'L|';
foreach ($map56Peer as $loopKey56Peer => $loopValue56Peer) {
    if ($loopKey56Peer === $scalarKey56Peer) {
        echo 's|', $loopValue56Peer, '|';
    } elseif ($loopKey56Peer === $firstKey56Peer) {
        echo 'o|', $loopValue56Peer->tag, '|';
    } else {
        echo 'a|', (int) ($loopValue56Peer[0][0] === $loopValue56Peer[1][2]), '|',
            $loopValue56Peer[0][1], '|';
    }
}
echo 'E|', (int) ($loopKey56Peer === $lastKey56Peer), '|',
    (int) ($loopValue56Peer[0][0] === $loopValue56Peer[1][2]), '|';
unset($map56Peer);
echo 'M|', (int) ($mapWatch56Peer->get() === NULL), '|',
    (int) ($firstChildWatch56Peer->get() === NULL), '|',
    (int) ($lastChildWatch56Peer->get() !== NULL), '|';
unset($lastKey56Peer, $firstKey56Peer, $scalarKey56Peer);
echo 'K|', (int) ($lastKeyWatch56Peer->get() !== NULL), '|',
    (int) ($firstKeyWatch56Peer->get() === NULL), '|';
unset($loopKey56Peer);
echo 'k|', (int) ($lastKeyWatch56Peer->get() === NULL), '|';
unset($loopValue56Peer);
echo 'F|', (int) ($lastChildWatch56Peer->get() === NULL), '|',
    (int) ($lastWatch56Peer->get() === NULL), '|';
