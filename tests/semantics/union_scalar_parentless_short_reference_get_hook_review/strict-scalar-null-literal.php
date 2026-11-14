<?php
declare(strict_types=1);
class OrderedScalar301PeerBox {
    public int|null $i { &get => $this->{'i'}; }
    public float|null $f { &get => $this->{"\x66"}; }
    public bool|null $b { &get => $this->{'b'}; }
    public string|null $s { &get => $this->{'s'}; }
}
$box301peer = new OrderedScalar301PeerBox();
$i301peer =& $box301peer->i;
$f301peer =& $box301peer->f;
$b301peer =& $box301peer->b;
$s301peer =& $box301peer->s;
echo $i301peer === null && $f301peer === null && $b301peer === null && $s301peer === null ? 'N|' : '?|';
$i301peer = 17;
$f301peer = 19;
$b301peer = true;
$s301peer = 'kept';
echo $i301peer === 17 && $f301peer === 19.0 && $b301peer === true && $s301peer === 'kept' ? 'V|' : '?|';
$copyi301peer = $i301peer;
$copyf301peer = $f301peer;
$copyb301peer = $b301peer;
$copys301peer = $s301peer;
$aliasi301peer =& $i301peer;
$aliasi301peer = 23;
$f301peer = 29;
$b301peer = false;
$s301peer = 'changed';
echo $copyi301peer === 17 && $copyf301peer === 19.0 && $copyb301peer === true && $copys301peer === 'kept' ? 'C|' : '?|';
try { $i301peer = 'bad'; }
catch (TypeError $error301peer) {
    echo $error301peer->getMessage() === 'Cannot assign string to reference held by property OrderedScalar301PeerBox::$i of type ?int' ? 'I|' : '?|';
}
try { $b301peer = 1; }
catch (TypeError $error301peer) {
    echo $error301peer->getMessage() === 'Cannot assign int to reference held by property OrderedScalar301PeerBox::$b of type ?bool' ? 'B|' : '?|';
}
try { $s301peer = 3; }
catch (TypeError $error301peer) {
    echo $error301peer->getMessage() === 'Cannot assign int to reference held by property OrderedScalar301PeerBox::$s of type ?string' ? 'S|' : '?|';
}
try { $f301peer = '31'; }
catch (TypeError $error301peer) {
    echo $error301peer->getMessage() === 'Cannot assign string to reference held by property OrderedScalar301PeerBox::$f of type ?float' ? 'F|' : '?|';
}
unset($error301peer);
echo $i301peer === 23 && $f301peer === 29.0 && $b301peer === false && $s301peer === 'changed' ? 'K|' : '?|';
$aliasi301peer = null;
$f301peer = null;
$b301peer = null;
$s301peer = null;
echo $i301peer === null && $f301peer === null && $b301peer === null && $s301peer === null && $copyi301peer === 17 && $copyf301peer === 19.0 && $copyb301peer === true && $copys301peer === 'kept' ? 'Q|' : '?|';
$i301peer = 37;
$f301peer = 41;
$b301peer = true;
$s301peer = 'live';
unset($box301peer);
$aliasi301peer = 'free-int';
$f301peer = [];
$b301peer = 67;
$s301peer = false;
echo $i301peer === 'free-int' && $f301peer === [] && $b301peer === 67 && $s301peer === false ? 'R|' : '?|';
unset($i301peer, $aliasi301peer, $f301peer, $b301peer, $s301peer);
unset($copyi301peer, $copyf301peer, $copyb301peer, $copys301peer);
echo 'E|';
