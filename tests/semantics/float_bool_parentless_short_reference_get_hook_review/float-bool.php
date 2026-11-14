<?php
declare(strict_types=1);
namespace Ns310StrictFloatBoolShortReferencePeer;
class Box310 {
    public float|bool $v = 0.0 {
        &get =>
            $this->{'v'};
    }
}
$box310peer = new Box310();
echo (array)$box310peer === ['v' => 0.0] ? 'I|' : 'BAD|';
$copy310peer = 'saved';
$copy310peer = $box310peer->v;
echo $copy310peer === 0.0 ? 'V|' : 'BAD|';
$copy310peer = false;
$a310peer =& $box310peer->v;
$b310peer =& $box310peer->v;
echo $a310peer === 0.0 && $b310peer === 0.0 && $copy310peer === false ? 'N|' : 'BAD|';
$a310peer = 17;
echo $a310peer === 17.0 && $b310peer === 17.0 ? 'J|' : 'BAD|';
$b310peer = 2.0;
echo $a310peer === 2.0 && $b310peer === 2.0 ? 'D|' : 'BAD|';
$a310peer = true;
echo $a310peer === true && $b310peer === true ? 'T|' : 'BAD|';
$b310peer = false;
echo $a310peer === false && $b310peer === false ? 'F|' : 'BAD|';
try { $a310peer = '12'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns310StrictFloatBoolShortReferencePeer\Box310::$v of type float|bool' && $a310peer === false && $b310peer === false ? 'S|' : 'BAD|';
}
try { $b310peer = '12.5'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns310StrictFloatBoolShortReferencePeer\Box310::$v of type float|bool' && $a310peer === false && $b310peer === false ? 'G|' : 'BAD|';
}
try { $a310peer = 'plain'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns310StrictFloatBoolShortReferencePeer\Box310::$v of type float|bool' && $a310peer === false && $b310peer === false ? 'P|' : 'BAD|';
}
try { $b310peer = ''; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns310StrictFloatBoolShortReferencePeer\Box310::$v of type float|bool' && $a310peer === false && $b310peer === false ? 'E|' : 'BAD|';
}
try { $a310peer = '0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns310StrictFloatBoolShortReferencePeer\Box310::$v of type float|bool' && $a310peer === false && $b310peer === false ? 'Q|' : 'BAD|';
}
try { $a310peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns310StrictFloatBoolShortReferencePeer\Box310::$v of type float|bool' && $a310peer === false && $b310peer === false ? 'L|' : 'BAD|';
}
try { $b310peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns310StrictFloatBoolShortReferencePeer\Box310::$v of type float|bool' && $a310peer === false && $b310peer === false ? 'A|' : 'BAD|';
}
try { $a310peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns310StrictFloatBoolShortReferencePeer\Box310::$v of type float|bool' && $a310peer === false && $b310peer === false ? 'O|' : 'BAD|';
}
unset($e);
$b310peer = 37;
echo $a310peer === 37.0 && $b310peer === 37.0 && $copy310peer === false ? 'K|' : 'BAD|';
unset($box310peer);
$a310peer = 23;
echo $a310peer === 23 && $b310peer === 23 && $copy310peer === false ? 'R|' : 'BAD|';
unset($a310peer, $b310peer, $copy310peer);
echo 'Z|';
