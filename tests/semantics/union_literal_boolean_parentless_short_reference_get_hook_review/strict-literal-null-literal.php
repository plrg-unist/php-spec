<?php
declare(strict_types=1);
class LiteralBoolean303PeerBox {
    public false|null $f { &get => $this->{"\x66"}; }
    public true|null $t { &get => $this->{'t'}; }
}
$box303peer = new LiteralBoolean303PeerBox();
$f303peer =& $box303peer->f;
$t303peer =& $box303peer->t;
echo $f303peer === null && $t303peer === null ? 'N|' : '?|';
$f303peer = false;
$t303peer = true;
echo $f303peer === false && $t303peer === true ? 'V|' : '?|';
$copyf303peer = $f303peer;
$copyt303peer = $t303peer;
$aliasf303peer =& $f303peer;
try { $f303peer = true; }
catch (TypeError $error303peer) {
    echo $error303peer->getMessage() === 'Cannot assign true to reference held by property LiteralBoolean303PeerBox::$f of type ?false' ? 'F|' : '?|';
}
try { $t303peer = false; }
catch (TypeError $error303peer) {
    echo $error303peer->getMessage() === 'Cannot assign false to reference held by property LiteralBoolean303PeerBox::$t of type ?true' ? 'T|' : '?|';
}
try { $aliasf303peer = 0; }
catch (TypeError $error303peer) {
    echo $error303peer->getMessage() === 'Cannot assign int to reference held by property LiteralBoolean303PeerBox::$f of type ?false' ? 'I|' : '?|';
}
try { $t303peer = 1; }
catch (TypeError $error303peer) {
    echo $error303peer->getMessage() === 'Cannot assign int to reference held by property LiteralBoolean303PeerBox::$t of type ?true' ? 'J|' : '?|';
}
$aliasf303peer = null;
$t303peer = null;
echo $f303peer === null && $t303peer === null && $copyf303peer === false && $copyt303peer === true ? 'Q|' : '?|';
$f303peer = false;
$t303peer = true;
unset($error303peer);
echo $f303peer === false && $t303peer === true && $copyf303peer === false && $copyt303peer === true ? 'K|' : '?|';
unset($box303peer);
$aliasf303peer = 0;
$t303peer = 1;
echo $f303peer === 0 && $t303peer === 1 && $copyf303peer === false && $copyt303peer === true ? 'R|' : '?|';
unset($f303peer, $aliasf303peer, $t303peer, $copyf303peer, $copyt303peer);
echo 'E|';
