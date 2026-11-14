<?php
declare(strict_types=1);
namespace Ns308StrictFloatStringShortReferencePeer;
class Box308 {
    public float|string $v = 0.0 {
        &get =>
            $this->{'v'};
    }
}
$box308peer = new Box308();
echo (array)$box308peer === ['v' => 0.0] ? 'I|' : 'BAD|';
$copy308peer = 'saved';
$copy308peer = $box308peer->v;
echo $copy308peer === 0.0 ? 'V|' : 'BAD|';
$copy308peer = false;
$a308peer =& $box308peer->v;
$b308peer =& $box308peer->v;
echo $a308peer === 0.0 && $b308peer === 0.0 && $copy308peer === false ? 'N|' : 'BAD|';
$a308peer = 2.0;
echo $b308peer === 2.0 ? 'D|' : 'BAD|';
$b308peer = '12';
echo $a308peer === '12' && $b308peer === '12' ? 'S|' : 'BAD|';
$a308peer = 'plain';
echo $a308peer === 'plain' && $b308peer === 'plain' ? 'P|' : 'BAD|';
$b308peer = 17;
echo $a308peer === 17.0 && $b308peer === 17.0 ? 'J|' : 'BAD|';
try { $a308peer = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns308StrictFloatStringShortReferencePeer\Box308::$v of type string|float' && $a308peer === 17.0 && $b308peer === 17.0 ? 'T|' : 'BAD|';
}
try { $b308peer = false; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign false to reference held by property Ns308StrictFloatStringShortReferencePeer\Box308::$v of type string|float' && $a308peer === 17.0 && $b308peer === 17.0 ? 'F|' : 'BAD|';
}
try { $a308peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns308StrictFloatStringShortReferencePeer\Box308::$v of type string|float' && $a308peer === 17.0 && $b308peer === 17.0 ? 'L|' : 'BAD|';
}
try { $b308peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns308StrictFloatStringShortReferencePeer\Box308::$v of type string|float' && $a308peer === 17.0 && $b308peer === 17.0 ? 'A|' : 'BAD|';
}
try { $a308peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns308StrictFloatStringShortReferencePeer\Box308::$v of type string|float' && $a308peer === 17.0 && $b308peer === 17.0 ? 'O|' : 'BAD|';
}
unset($e);
$b308peer = 'kept';
echo $a308peer === 'kept' && $copy308peer === false ? 'K|' : 'BAD|';
unset($box308peer);
$a308peer = false;
echo $b308peer === false && $copy308peer === false ? 'R|' : 'BAD|';
unset($a308peer, $b308peer, $copy308peer);
echo 'Z|';
