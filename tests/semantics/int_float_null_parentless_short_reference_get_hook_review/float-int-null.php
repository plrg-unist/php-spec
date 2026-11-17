<?php
declare(strict_types=1);
namespace Ns317StrictFloatIntNullShortReferencePeer;
class Box317peer {
    public float|int|null $v {
        &get =>
            $this->{'v'};
    }
}
$box317peer = new Box317peer();
echo (array)$box317peer === [] ? 'U|' : 'BAD|';
$copy317peer = 'saved';
$copy317peer = $box317peer->v;
echo $copy317peer === null ? 'V|' : 'BAD|';
echo (array)$box317peer === ['v' => null] ? 'P|' : 'BAD|';
$copy317peer = false;
$a317peer =& $box317peer->v;
$b317peer =& $box317peer->v;
echo $a317peer === null && $b317peer === null && $copy317peer === false ? 'N|' : 'BAD|';
$a317peer = 17;
echo $a317peer === 17 && $b317peer === 17 ? 'J|' : 'BAD|';
$b317peer = 2.0;
echo $a317peer === 2.0 && $b317peer === 2.0 ? 'D|' : 'BAD|';
$probe_float317peer = $box317peer->v;
echo $probe_float317peer === 2.0 && $a317peer === 2.0 && $b317peer === 2.0 && $copy317peer === false ? 'G|' : 'BAD|';
unset($probe_float317peer);
try { $a317peer = '12'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns317StrictFloatIntNullShortReferencePeer\Box317peer::$v of type int|float|null' && $a317peer === 2.0 && $b317peer === 2.0 ? 'S|' : 'BAD|';
}
try { $b317peer = '12.5'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns317StrictFloatIntNullShortReferencePeer\Box317peer::$v of type int|float|null' && $a317peer === 2.0 && $b317peer === 2.0 ? 'Q|' : 'BAD|';
}
try { $a317peer = '2e0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns317StrictFloatIntNullShortReferencePeer\Box317peer::$v of type int|float|null' && $a317peer === 2.0 && $b317peer === 2.0 ? 'X|' : 'BAD|';
}
try { $b317peer = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns317StrictFloatIntNullShortReferencePeer\Box317peer::$v of type int|float|null' && $a317peer === 2.0 && $b317peer === 2.0 ? 'T|' : 'BAD|';
}
try { $a317peer = false; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign false to reference held by property Ns317StrictFloatIntNullShortReferencePeer\Box317peer::$v of type int|float|null' && $a317peer === 2.0 && $b317peer === 2.0 ? 'F|' : 'BAD|';
}
try { $b317peer = 'bad'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns317StrictFloatIntNullShortReferencePeer\Box317peer::$v of type int|float|null' && $a317peer === 2.0 && $b317peer === 2.0 ? 'B|' : 'BAD|';
}
$a317peer = null;
echo $a317peer === null && $b317peer === null ? 'L|' : 'BAD|';
$probe_null317peer = $box317peer->v;
echo $probe_null317peer === null && $a317peer === null && $b317peer === null && $copy317peer === false ? 'H|' : 'BAD|';
unset($probe_null317peer);
try { $b317peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns317StrictFloatIntNullShortReferencePeer\Box317peer::$v of type int|float|null' && $a317peer === null && $b317peer === null ? 'A|' : 'BAD|';
}
try { $a317peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns317StrictFloatIntNullShortReferencePeer\Box317peer::$v of type int|float|null' && $a317peer === null && $b317peer === null ? 'O|' : 'BAD|';
}
unset($e);
$b317peer = 37;
echo $a317peer === 37 && $b317peer === 37 && $copy317peer === false ? 'K|' : 'BAD|';
unset($box317peer);
$a317peer = 'free';
echo $a317peer === 'free' && $b317peer === 'free' && $copy317peer === false ? 'R|' : 'BAD|';
unset($a317peer, $b317peer, $copy317peer);
echo 'Z|';
