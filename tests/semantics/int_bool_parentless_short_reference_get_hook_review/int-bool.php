<?php
declare(strict_types=1);
namespace Ns309StrictIntBoolShortReferencePeer;
class Box309 {
    public int|bool $v = 0 {
        &get =>
            $this->{'v'};
    }
}
$box309peer = new Box309();
echo (array)$box309peer === ['v' => 0] ? 'I|' : 'BAD|';
$copy309peer = 'saved';
$copy309peer = $box309peer->v;
echo $copy309peer === 0 ? 'V|' : 'BAD|';
$copy309peer = false;
$a309peer =& $box309peer->v;
$b309peer =& $box309peer->v;
echo $a309peer === 0 && $b309peer === 0 && $copy309peer === false ? 'N|' : 'BAD|';
$a309peer = 17;
echo $b309peer === 17 ? 'J|' : 'BAD|';
$b309peer = true;
echo $a309peer === true && $b309peer === true ? 'T|' : 'BAD|';
$a309peer = false;
echo $a309peer === false && $b309peer === false ? 'F|' : 'BAD|';
try { $b309peer = 2.0; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign float to reference held by property Ns309StrictIntBoolShortReferencePeer\Box309::$v of type int|bool' && $a309peer === false && $b309peer === false ? 'D|' : 'BAD|';
}
try { $a309peer = '12'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns309StrictIntBoolShortReferencePeer\Box309::$v of type int|bool' && $a309peer === false && $b309peer === false ? 'S|' : 'BAD|';
}
try { $b309peer = 'plain'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns309StrictIntBoolShortReferencePeer\Box309::$v of type int|bool' && $a309peer === false && $b309peer === false ? 'P|' : 'BAD|';
}
try { $a309peer = ''; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns309StrictIntBoolShortReferencePeer\Box309::$v of type int|bool' && $a309peer === false && $b309peer === false ? 'E|' : 'BAD|';
}
try { $b309peer = '0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns309StrictIntBoolShortReferencePeer\Box309::$v of type int|bool' && $a309peer === false && $b309peer === false ? 'Q|' : 'BAD|';
}
try { $a309peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns309StrictIntBoolShortReferencePeer\Box309::$v of type int|bool' && $a309peer === false && $b309peer === false ? 'L|' : 'BAD|';
}
try { $b309peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns309StrictIntBoolShortReferencePeer\Box309::$v of type int|bool' && $a309peer === false && $b309peer === false ? 'A|' : 'BAD|';
}
try { $a309peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns309StrictIntBoolShortReferencePeer\Box309::$v of type int|bool' && $a309peer === false && $b309peer === false ? 'O|' : 'BAD|';
}
unset($e);
$b309peer = 37;
echo $a309peer === 37 && $copy309peer === false ? 'K|' : 'BAD|';
unset($box309peer);
$a309peer = 3.5;
echo $b309peer === 3.5 && $copy309peer === false ? 'R|' : 'BAD|';
unset($a309peer, $b309peer, $copy309peer);
echo 'Z|';
