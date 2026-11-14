<?php
declare(strict_types=1);
namespace Ns311StrictStringBoolShortReferencePeer;
class Box311 {
    public string|bool $v {
        &get =>
            $this->{'v'};
    }
}
$box311peer = new Box311();
echo (array)$box311peer === [] ? 'U|' : 'BAD|';
$copy311peer = 'saved';
try { $copy311peer = $box311peer->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns311StrictStringBoolShortReferencePeer\Box311::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy311peer === 'saved' && (array)$box311peer === [] ? 'P|' : 'BAD|';
unset($e);
$box311peer->v = false;
$copy311peer = $box311peer->v;
echo $copy311peer === false ? 'V|' : 'BAD|';
$copy311peer = 17;
$a311peer =& $box311peer->v;
$b311peer =& $box311peer->v;
echo $a311peer === false && $b311peer === false && $copy311peer === 17 ? 'N|' : 'BAD|';
$a311peer = true;
echo $a311peer === true && $b311peer === true ? 'T|' : 'BAD|';
$b311peer = false;
echo $a311peer === false && $b311peer === false ? 'F|' : 'BAD|';
$a311peer = 'plain';
echo $a311peer === 'plain' && $b311peer === 'plain' ? 'P|' : 'BAD|';
$b311peer = '12';
echo $a311peer === '12' && $b311peer === '12' ? 'S|' : 'BAD|';
$a311peer = '12.5';
echo $a311peer === '12.5' && $b311peer === '12.5' ? 'H|' : 'BAD|';
$b311peer = '';
echo $a311peer === '' && $b311peer === '' ? 'E|' : 'BAD|';
$a311peer = '0';
echo $a311peer === '0' && $b311peer === '0' ? 'Q|' : 'BAD|';
$probe311peer = $box311peer->v;
echo $probe311peer === '0' && $a311peer === '0' && $b311peer === '0' && $copy311peer === 17 ? 'G|' : 'BAD|';
unset($probe311peer);
try { $a311peer = 17; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns311StrictStringBoolShortReferencePeer\Box311::$v of type string|bool' && $a311peer === '0' && $b311peer === '0' ? 'J|' : 'BAD|';
}
try { $b311peer = 2.5; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign float to reference held by property Ns311StrictStringBoolShortReferencePeer\Box311::$v of type string|bool' && $a311peer === '0' && $b311peer === '0' ? 'D|' : 'BAD|';
}
try { $a311peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns311StrictStringBoolShortReferencePeer\Box311::$v of type string|bool' && $a311peer === '0' && $b311peer === '0' ? 'L|' : 'BAD|';
}
try { $b311peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns311StrictStringBoolShortReferencePeer\Box311::$v of type string|bool' && $a311peer === '0' && $b311peer === '0' ? 'A|' : 'BAD|';
}
try { $a311peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns311StrictStringBoolShortReferencePeer\Box311::$v of type string|bool' && $a311peer === '0' && $b311peer === '0' ? 'O|' : 'BAD|';
}
unset($e);
$b311peer = 'kept';
echo $a311peer === 'kept' && $b311peer === 'kept' && $copy311peer === 17 ? 'K|' : 'BAD|';
unset($box311peer);
$a311peer = 23;
echo $a311peer === 23 && $b311peer === 23 && $copy311peer === 17 ? 'R|' : 'BAD|';
unset($a311peer, $b311peer, $copy311peer);
echo 'Z|';
