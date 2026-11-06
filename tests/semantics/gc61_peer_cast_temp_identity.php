<?php
class GC61EmptyPeer {}
class GC61SentinelPeer { public function __destruct() { echo 'D|'; } }
$object61Peer = new GC61EmptyPeer;
$sentinel61Peer = new GC61SentinelPeer;
(array) $object61Peer;
echo 'B|';
echo (array) $object61Peer !== [17];
echo '|';
$shape61Peer = (array) $object61Peer;
echo 'A|', $shape61Peer !== [17], '|';
unset($shape61Peer, $object61Peer);
unset($sentinel61Peer);
echo 'Z|';
