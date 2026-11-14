<?php
declare(strict_types=1);
class LiteralBoolean302PeerBox {
    public false $f = false { &get => $this->{"\x66"}; }
    public true $t = true { &get => $this->{'t'}; }
}
$box302peer = new LiteralBoolean302PeerBox();
$f302peer =& $box302peer->f;
$t302peer =& $box302peer->t;
echo $f302peer === false && $t302peer === true ? 'V|' : '?|';
$copyf302peer = $f302peer;
$copyt302peer = $t302peer;
$aliasf302peer =& $f302peer;
try { $f302peer = true; }
catch (TypeError $error302peer) {
    echo $error302peer->getMessage() === 'Cannot assign true to reference held by property LiteralBoolean302PeerBox::$f of type false' ? 'F|' : '?|';
}
try { $t302peer = false; }
catch (TypeError $error302peer) {
    echo $error302peer->getMessage() === 'Cannot assign false to reference held by property LiteralBoolean302PeerBox::$t of type true' ? 'T|' : '?|';
}
try { $aliasf302peer = 0; }
catch (TypeError $error302peer) {
    echo $error302peer->getMessage() === 'Cannot assign int to reference held by property LiteralBoolean302PeerBox::$f of type false' ? 'I|' : '?|';
}
try { $t302peer = 1; }
catch (TypeError $error302peer) {
    echo $error302peer->getMessage() === 'Cannot assign int to reference held by property LiteralBoolean302PeerBox::$t of type true' ? 'J|' : '?|';
}
try { $f302peer = null; }
catch (TypeError $error302peer) { echo 'N|'; }
try { $t302peer = null; }
catch (TypeError $error302peer) { echo 'M|'; }
unset($error302peer);
echo $f302peer === false && $t302peer === true && $copyf302peer === false && $copyt302peer === true ? 'K|' : '?|';
unset($box302peer);
$aliasf302peer = 0;
$t302peer = 1;
echo $f302peer === 0 && $t302peer === 1 && $copyf302peer === false && $copyt302peer === true ? 'R|' : '?|';
unset($f302peer, $aliasf302peer, $t302peer, $copyf302peer, $copyt302peer);
echo 'E|';
