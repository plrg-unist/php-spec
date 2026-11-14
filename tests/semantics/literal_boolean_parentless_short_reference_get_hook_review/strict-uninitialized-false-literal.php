<?php
declare(strict_types=1);
class LiteralBoolean302UninitPeerBox {
    public false $f { &get => $this->{'f'}; }
}
$box302peer = new LiteralBoolean302UninitPeerBox();
$old302peer = 'old';
$probe302peer =& $old302peer;
$shadow302peer =& $probe302peer;
try { $probe302peer =& $box302peer->f; }
catch (Error $error302peer) {
    echo $error302peer->getMessage() === 'Cannot access uninitialized non-nullable property LiteralBoolean302UninitPeerBox::$f by reference' ? 'U|' : '?|';
}
echo $probe302peer === 'old' && $shadow302peer === 'old' ? 'P|' : '?|';
$shadow302peer = 37;
echo $probe302peer === 37 && $old302peer === 37 ? 'W|' : '?|';
$box302peer->f = false;
$probe302peer =& $box302peer->f;
echo $probe302peer === false && $old302peer === 37 && $shadow302peer === 37 ? 'A|' : '?|';
try { $probe302peer = true; }
catch (TypeError $error302peer) {
    echo $error302peer->getMessage() === 'Cannot assign true to reference held by property LiteralBoolean302UninitPeerBox::$f of type false' ? 'T|' : '?|';
}
unset($box302peer);
$probe302peer = 'free';
echo $probe302peer === 'free' && $old302peer === 37 && $shadow302peer === 37 ? 'R|' : '?|';
unset($probe302peer, $old302peer, $shadow302peer, $error302peer);
echo 'E|';
