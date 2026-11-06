<?php
class GC61EmptyPeer {}
$object61Peer = new GC61EmptyPeer;
echo 'B|';
echo (array) $object61Peer !== [17];
echo '|';
$shape61Peer = (array) $object61Peer;
echo 'A|', $shape61Peer !== [17], '|';
unset($shape61Peer, $object61Peer);
echo 'Z|';
