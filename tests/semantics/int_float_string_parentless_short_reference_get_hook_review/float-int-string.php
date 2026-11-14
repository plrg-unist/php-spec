<?php
declare(strict_types=1);
namespace Ns313StrictFloatIntStringReferencePeer;
class Box313Peer {
    public float|int|string $v = 0 {
        &get =>
            $this->{'v'};
    }
}
$box313peer = new Box313Peer();
echo (array)$box313peer === ['v' => 0] ? 'I|' : 'BAD|';
$copy313peer = 'saved';
$copy313peer = $box313peer->v;
echo $copy313peer === 0 ? 'V|' : 'BAD|';
$copy313peer = 17;
$a313peer =& $box313peer->v;
$b313peer =& $box313peer->v;
echo $a313peer === 0 && $b313peer === 0 && $copy313peer === 17 ? 'N|' : 'BAD|';
$a313peer = 23;
echo $a313peer === 23 && $b313peer === 23 ? 'J|' : 'BAD|';
$b313peer = 2.5;
echo $a313peer === 2.5 && $b313peer === 2.5 ? 'D|' : 'BAD|';
$probe_float313peer = $box313peer->v;
echo $probe_float313peer === 2.5 && $a313peer === 2.5 && $b313peer === 2.5 && $copy313peer === 17 ? 'G|' : 'BAD|';
unset($probe_float313peer);
$a313peer = 'plain';
echo $a313peer === 'plain' && $b313peer === 'plain' ? 'P|' : 'BAD|';
$probe_string313peer = $box313peer->v;
echo $probe_string313peer === 'plain' && $a313peer === 'plain' && $b313peer === 'plain' && $copy313peer === 17 ? 'H|' : 'BAD|';
unset($probe_string313peer);
$a313peer = '12';
echo $a313peer === '12' && $b313peer === '12' ? 'S|' : 'BAD|';
$b313peer = '12.5';
echo $a313peer === '12.5' && $b313peer === '12.5' ? 'L|' : 'BAD|';
$a313peer = '2e0';
echo $a313peer === '2e0' && $b313peer === '2e0' ? 'X|' : 'BAD|';
$b313peer = '';
echo $a313peer === '' && $b313peer === '' ? 'E|' : 'BAD|';
$a313peer = '0';
echo $a313peer === '0' && $b313peer === '0' ? 'Q|' : 'BAD|';
try { $b313peer = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns313StrictFloatIntStringReferencePeer\Box313Peer::$v of type string|int|float' && $a313peer === '0' && $b313peer === '0' ? 'T|' : 'BAD|';
}
try { $a313peer = false; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign false to reference held by property Ns313StrictFloatIntStringReferencePeer\Box313Peer::$v of type string|int|float' && $a313peer === '0' && $b313peer === '0' ? 'F|' : 'BAD|';
}
try { $a313peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns313StrictFloatIntStringReferencePeer\Box313Peer::$v of type string|int|float' && $a313peer === '0' && $b313peer === '0' ? 'U|' : 'BAD|';
}
try { $b313peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns313StrictFloatIntStringReferencePeer\Box313Peer::$v of type string|int|float' && $a313peer === '0' && $b313peer === '0' ? 'A|' : 'BAD|';
}
try { $a313peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns313StrictFloatIntStringReferencePeer\Box313Peer::$v of type string|int|float' && $a313peer === '0' && $b313peer === '0' ? 'O|' : 'BAD|';
}
unset($e);
$b313peer = 37;
echo $a313peer === 37 && $b313peer === 37 && $copy313peer === 17 ? 'K|' : 'BAD|';
unset($box313peer);
$a313peer = true;
echo $a313peer === true && $b313peer === true && $copy313peer === 17 ? 'R|' : 'BAD|';
unset($a313peer, $b313peer, $copy313peer);
echo 'Z|';
