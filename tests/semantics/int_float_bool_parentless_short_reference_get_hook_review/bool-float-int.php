<?php
declare(strict_types=1);
namespace Ns312StrictBoolFloatIntReferencePeer;
class Box312Peer {
    public bool|float|int $v {
        &get =>
            $this->{'v'};
    }
}
$box312peer = new Box312Peer();
echo (array)$box312peer === [] ? 'U|' : 'BAD|';
$copy312peer = 'saved';
try { $copy312peer = $box312peer->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy312peer === 'saved' && (array)$box312peer === [] ? 'P|' : 'BAD|';
unset($e);
$box312peer->v = 0;
$copy312peer = $box312peer->v;
echo $copy312peer === 0 ? 'V|' : 'BAD|';
$copy312peer = 17;
$a312peer =& $box312peer->v;
$b312peer =& $box312peer->v;
echo $a312peer === 0 && $b312peer === 0 && $copy312peer === 17 ? 'N|' : 'BAD|';
$a312peer = 23;
echo $a312peer === 23 && $b312peer === 23 ? 'J|' : 'BAD|';
$b312peer = 2.5;
echo $a312peer === 2.5 && $b312peer === 2.5 ? 'D|' : 'BAD|';
$probe_float312peer = $box312peer->v;
echo $probe_float312peer === 2.5 && $a312peer === 2.5 && $b312peer === 2.5 && $copy312peer === 17 ? 'G|' : 'BAD|';
unset($probe_float312peer);
$a312peer = true;
echo $a312peer === true && $b312peer === true ? 'T|' : 'BAD|';
$b312peer = false;
echo $a312peer === false && $b312peer === false ? 'F|' : 'BAD|';
$probe_bool312peer = $box312peer->v;
echo $probe_bool312peer === false && $a312peer === false && $b312peer === false && $copy312peer === 17 ? 'H|' : 'BAD|';
unset($probe_bool312peer);
try { $a312peer = '12'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v of type int|float|bool' && $a312peer === false && $b312peer === false ? 'S|' : 'BAD|';
}
try { $b312peer = '12.5'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v of type int|float|bool' && $a312peer === false && $b312peer === false ? 'L|' : 'BAD|';
}
try { $a312peer = '2e0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v of type int|float|bool' && $a312peer === false && $b312peer === false ? 'X|' : 'BAD|';
}
try { $b312peer = 'plain'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v of type int|float|bool' && $a312peer === false && $b312peer === false ? 'P|' : 'BAD|';
}
try { $a312peer = ''; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v of type int|float|bool' && $a312peer === false && $b312peer === false ? 'E|' : 'BAD|';
}
try { $b312peer = '0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v of type int|float|bool' && $a312peer === false && $b312peer === false ? 'Q|' : 'BAD|';
}
try { $a312peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v of type int|float|bool' && $a312peer === false && $b312peer === false ? 'U|' : 'BAD|';
}
try { $b312peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v of type int|float|bool' && $a312peer === false && $b312peer === false ? 'A|' : 'BAD|';
}
try { $a312peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns312StrictBoolFloatIntReferencePeer\Box312Peer::$v of type int|float|bool' && $a312peer === false && $b312peer === false ? 'O|' : 'BAD|';
}
unset($e);
$b312peer = 37;
echo $a312peer === 37 && $b312peer === 37 && $copy312peer === 17 ? 'K|' : 'BAD|';
unset($box312peer);
$a312peer = 'detached';
echo $a312peer === 'detached' && $b312peer === 'detached' && $copy312peer === 17 ? 'R|' : 'BAD|';
unset($a312peer, $b312peer, $copy312peer);
echo 'Z|';
