<?php
declare(strict_types=1);
class Null304PeerBox {
    public null $v = null { &get => $this->{"\x76"}; }
}
$box304peer = new Null304PeerBox();
echo (array)$box304peer === ['v' => null] ? 'B|' : '?|';
$copy304peer = $box304peer->v;
echo $copy304peer === null && (array)$box304peer === ['v' => null] ? 'C|' : '?|';
$copy304peer = false;
$ref304peer =& $box304peer->v;
$alias304peer =& $ref304peer;
echo $ref304peer === null && $alias304peer === null && $copy304peer === false ? 'V|' : '?|';
try { $ref304peer = false; }
catch (TypeError $error304peer) {
    echo $error304peer->getMessage() === 'Cannot assign false to reference held by property Null304PeerBox::$v of type null' ? 'F|' : '?|';
}
try { $alias304peer = true; }
catch (TypeError $error304peer) {
    echo $error304peer->getMessage() === 'Cannot assign true to reference held by property Null304PeerBox::$v of type null' ? 'T|' : '?|';
}
try { $ref304peer = 0; }
catch (TypeError $error304peer) {
    echo $error304peer->getMessage() === 'Cannot assign int to reference held by property Null304PeerBox::$v of type null' ? 'I|' : '?|';
}
try { $alias304peer = '0'; }
catch (TypeError $error304peer) {
    echo $error304peer->getMessage() === 'Cannot assign string to reference held by property Null304PeerBox::$v of type null' ? 'S|' : '?|';
}
try { $ref304peer = []; }
catch (TypeError $error304peer) {
    echo $error304peer->getMessage() === 'Cannot assign array to reference held by property Null304PeerBox::$v of type null' ? 'A|' : '?|';
}
$alias304peer = null;
unset($error304peer);
echo $ref304peer === null && $alias304peer === null && $copy304peer === false ? 'K|' : '?|';
unset($box304peer);
$ref304peer = 37;
echo $alias304peer === 37 && $copy304peer === false ? 'R|' : '?|';
unset($ref304peer, $alias304peer, $copy304peer);
echo 'E|';
