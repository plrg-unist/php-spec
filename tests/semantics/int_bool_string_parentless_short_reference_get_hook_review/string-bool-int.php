<?php
declare(strict_types=1);
namespace Ns314StrictStringBoolIntReferencePeer;
class Box314Peer {
    public string|bool|int $v {
        &get =>
            $this->{'v'};
    }
}
$box314peer = new Box314Peer();
echo (array)$box314peer === [] ? 'U|' : 'BAD|';
$copy314peer = 'saved';
try { $copy314peer = $box314peer->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns314StrictStringBoolIntReferencePeer\Box314Peer::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy314peer === 'saved' && (array)$box314peer === [] ? 'P|' : 'BAD|';
unset($e);
$box314peer->v = 0;
$copy314peer = $box314peer->v;
echo $copy314peer === 0 ? 'V|' : 'BAD|';
$copy314peer = 17;
$a314peer =& $box314peer->v;
$b314peer =& $box314peer->v;
echo $a314peer === 0 && $b314peer === 0 && $copy314peer === 17 ? 'N|' : 'BAD|';
$a314peer = 23;
echo $a314peer === 23 && $b314peer === 23 ? 'J|' : 'BAD|';
$b314peer = true;
echo $a314peer === true && $b314peer === true ? 'D|' : 'BAD|';
$probe_bool314peer = $box314peer->v;
echo $probe_bool314peer === true && $a314peer === true && $b314peer === true && $copy314peer === 17 ? 'G|' : 'BAD|';
unset($probe_bool314peer);
$a314peer = false;
echo $a314peer === false && $b314peer === false ? 'F|' : 'BAD|';
$a314peer = 'plain';
echo $a314peer === 'plain' && $b314peer === 'plain' ? 'P|' : 'BAD|';
$probe_string314peer = $box314peer->v;
echo $probe_string314peer === 'plain' && $a314peer === 'plain' && $b314peer === 'plain' && $copy314peer === 17 ? 'H|' : 'BAD|';
unset($probe_string314peer);
$a314peer = '12';
echo $a314peer === '12' && $b314peer === '12' ? 'S|' : 'BAD|';
$b314peer = '12.5';
echo $a314peer === '12.5' && $b314peer === '12.5' ? 'L|' : 'BAD|';
$a314peer = '2e0';
echo $a314peer === '2e0' && $b314peer === '2e0' ? 'X|' : 'BAD|';
$b314peer = '';
echo $a314peer === '' && $b314peer === '' ? 'E|' : 'BAD|';
$a314peer = '0';
echo $a314peer === '0' && $b314peer === '0' ? 'Q|' : 'BAD|';
try { $b314peer = 2.0; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign float to reference held by property Ns314StrictStringBoolIntReferencePeer\Box314Peer::$v of type string|int|bool' && $a314peer === '0' && $b314peer === '0' ? 'T|' : 'BAD|';
}
try { $a314peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns314StrictStringBoolIntReferencePeer\Box314Peer::$v of type string|int|bool' && $a314peer === '0' && $b314peer === '0' ? 'U|' : 'BAD|';
}
try { $b314peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns314StrictStringBoolIntReferencePeer\Box314Peer::$v of type string|int|bool' && $a314peer === '0' && $b314peer === '0' ? 'A|' : 'BAD|';
}
try { $a314peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns314StrictStringBoolIntReferencePeer\Box314Peer::$v of type string|int|bool' && $a314peer === '0' && $b314peer === '0' ? 'O|' : 'BAD|';
}
unset($e);
$b314peer = 37;
echo $a314peer === 37 && $b314peer === 37 && $copy314peer === 17 ? 'K|' : 'BAD|';
unset($box314peer);
$a314peer = 2.5;
echo $a314peer === 2.5 && $b314peer === 2.5 && $copy314peer === 17 ? 'R|' : 'BAD|';
unset($a314peer, $b314peer, $copy314peer);
echo 'Z|';
