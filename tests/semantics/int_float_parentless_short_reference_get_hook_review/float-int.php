<?php
declare(strict_types=1);
namespace Ns307StrictFloatIntShortReferencePeer;
class Box307 {
    public float|int $v {
        &get =>
            $this->{'v'};
    }
}
$box307peer = new Box307();
echo (array)$box307peer === [] ? 'U|' : 'BAD|';
$copy307peer = 'saved';
try { $copy307peer = $box307peer->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns307StrictFloatIntShortReferencePeer\Box307::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy307peer === 'saved' && (array)$box307peer === [] ? 'P|' : 'BAD|';
unset($e);
$box307peer->v = 0;
$copy307peer = $box307peer->v;
echo $copy307peer === 0 ? 'V|' : 'BAD|';
$copy307peer = false;
$a307peer =& $box307peer->v;
$b307peer =& $box307peer->v;
echo $a307peer === 0 && $b307peer === 0 && $copy307peer === false ? 'N|' : 'BAD|';
$a307peer = 17;
echo $b307peer === 17 ? 'J|' : 'BAD|';
$b307peer = 2.0;
echo $a307peer === 2.0 ? 'D|' : 'BAD|';
try { $a307peer = '12'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns307StrictFloatIntShortReferencePeer\Box307::$v of type int|float' && $a307peer === 2.0 && $b307peer === 2.0 ? 'S|' : 'BAD|';
}
try { $b307peer = '12.5'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns307StrictFloatIntShortReferencePeer\Box307::$v of type int|float' && $a307peer === 2.0 && $b307peer === 2.0 ? 'Q|' : 'BAD|';
}
try { $a307peer = '2e0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns307StrictFloatIntShortReferencePeer\Box307::$v of type int|float' && $a307peer === 2.0 && $b307peer === 2.0 ? 'X|' : 'BAD|';
}
try { $b307peer = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns307StrictFloatIntShortReferencePeer\Box307::$v of type int|float' && $a307peer === 2.0 && $b307peer === 2.0 ? 'T|' : 'BAD|';
}
try { $a307peer = false; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign false to reference held by property Ns307StrictFloatIntShortReferencePeer\Box307::$v of type int|float' && $a307peer === 2.0 && $b307peer === 2.0 ? 'F|' : 'BAD|';
}
try { $b307peer = 'bad'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns307StrictFloatIntShortReferencePeer\Box307::$v of type int|float' && $a307peer === 2.0 && $b307peer === 2.0 ? 'B|' : 'BAD|';
}
try { $a307peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns307StrictFloatIntShortReferencePeer\Box307::$v of type int|float' && $a307peer === 2.0 && $b307peer === 2.0 ? 'L|' : 'BAD|';
}
try { $b307peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns307StrictFloatIntShortReferencePeer\Box307::$v of type int|float' && $a307peer === 2.0 && $b307peer === 2.0 ? 'A|' : 'BAD|';
}
try { $a307peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns307StrictFloatIntShortReferencePeer\Box307::$v of type int|float' && $a307peer === 2.0 && $b307peer === 2.0 ? 'O|' : 'BAD|';
}
unset($e);
$b307peer = 37;
echo $a307peer === 37 && $copy307peer === false ? 'K|' : 'BAD|';
unset($box307peer);
$a307peer = false;
echo $b307peer === false && $copy307peer === false ? 'R|' : 'BAD|';
unset($a307peer, $b307peer, $copy307peer);
echo 'Z|';
