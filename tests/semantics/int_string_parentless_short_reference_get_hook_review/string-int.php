<?php
declare(strict_types=1);
namespace Ns306StrictStringIntShortReferencePeer;
class Box306 {
    public string|int $v {
        &get =>
            $this->{'v'};
    }
}
$box306peer = new Box306();
echo (array)$box306peer === [] ? 'U|' : 'BAD|';
$copy306peer = 'saved';
try { $copy306peer = $box306peer->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns306StrictStringIntShortReferencePeer\Box306::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy306peer === 'saved' && (array)$box306peer === [] ? 'P|' : 'BAD|';
unset($e);
$box306peer->v = 0;
$copy306peer = $box306peer->v;
echo $copy306peer === 0 && (array)$box306peer === ['v' => 0] ? 'V|' : 'BAD|';
$copy306peer = false;
$a306peer =& $box306peer->v;
$b306peer =& $box306peer->v;
echo $a306peer === 0 && $b306peer === 0 && $copy306peer === false ? 'N|' : 'BAD|';
$a306peer = '12';
echo $b306peer === '12' ? 'S|' : 'BAD|';
$b306peer = 17;
echo $a306peer === 17 ? 'J|' : 'BAD|';
try { $a306peer = 2.0; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign float to reference held by property Ns306StrictStringIntShortReferencePeer\Box306::$v of type string|int' && $a306peer === 17 && $b306peer === 17 ? 'D|' : 'BAD|';
}
try { $b306peer = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns306StrictStringIntShortReferencePeer\Box306::$v of type string|int' && $a306peer === 17 && $b306peer === 17 ? 'T|' : 'BAD|';
}
try { $a306peer = false; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign false to reference held by property Ns306StrictStringIntShortReferencePeer\Box306::$v of type string|int' && $a306peer === 17 && $b306peer === 17 ? 'F|' : 'BAD|';
}
try { $a306peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns306StrictStringIntShortReferencePeer\Box306::$v of type string|int' ? 'L|' : 'BAD|';
}
try { $b306peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns306StrictStringIntShortReferencePeer\Box306::$v of type string|int' ? 'A|' : 'BAD|';
}
try { $a306peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns306StrictStringIntShortReferencePeer\Box306::$v of type string|int' ? 'O|' : 'BAD|';
}
unset($e);
$b306peer = 37;
echo $a306peer === 37 && $copy306peer === false ? 'K|' : 'BAD|';
unset($box306peer);
$a306peer = false;
echo $b306peer === false && $copy306peer === false ? 'R|' : 'BAD|';
unset($a306peer, $b306peer, $copy306peer);
echo 'Z|';
