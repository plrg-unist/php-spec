<?php
declare(strict_types=1);
class Mixed305PeerBox {
    public mixed $v { &get => $this->{"\x76"}; }
}
$box305peer = new Mixed305PeerBox();
echo (array)$box305peer === [] ? 'B|' : '?|';
$copy305peer = $box305peer->v;
echo $copy305peer === null && (array)$box305peer === ['v' => null] ? 'C|' : '?|';
$copy305peer = false;
$ref305peer =& $box305peer->v;
$alias305peer =& $ref305peer;
echo $ref305peer === null && $alias305peer === null && $copy305peer === false ? 'V|' : '?|';
$ref305peer = false;
echo $alias305peer === false ? 'F|' : '?|';
$alias305peer = true;
echo $ref305peer === true ? 'T|' : '?|';
$ref305peer = 0;
echo $alias305peer === 0 ? 'I|' : '?|';
$alias305peer = '0';
echo $ref305peer === '0' ? 'S|' : '?|';
$ref305peer = 1.5;
echo $alias305peer === 1.5 ? 'D|' : '?|';
$alias305peer = null;
echo $ref305peer === null ? 'N|' : '?|';
$ref305peer = [1];
$arraycopy305peer = $box305peer->v;
$alias305peer[0] = 2;
echo $arraycopy305peer === [1] && $ref305peer === [2] && $box305peer->v === [2] ? 'A|' : '?|';
$ref305peer = new \stdClass();
$objectcopy305peer = $box305peer->v;
$objectcopy305peer->value = 3;
echo $alias305peer === $objectcopy305peer && $alias305peer->value === 3 ? 'O|' : '?|';
$alias305peer = 37;
echo $ref305peer === 37 && $copy305peer === false && $arraycopy305peer === [1] && $objectcopy305peer->value === 3 ? 'K|' : '?|';
unset($box305peer);
$ref305peer = 'tail';
echo $alias305peer === 'tail' && $copy305peer === false && $arraycopy305peer === [1] && $objectcopy305peer->value === 3 ? 'R|' : '?|';
unset($ref305peer, $alias305peer, $copy305peer, $arraycopy305peer, $objectcopy305peer);
echo 'E|';
