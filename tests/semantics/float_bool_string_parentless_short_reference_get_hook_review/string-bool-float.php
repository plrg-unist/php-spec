<?php
declare(strict_types=1);
namespace Ns315StrictStringBoolFloatReferencePeer;
class Box315Peer {
    public string|bool|float $v {
        &get =>
            $this->{'v'};
    }
}
$box315peer = new Box315Peer();
echo (array)$box315peer === [] ? 'U|' : 'BAD|';
$copy315peer = 'saved';
try { $copy315peer = $box315peer->v; } catch (\Error $e) {
    echo $e->getMessage() === 'Cannot access uninitialized non-nullable property Ns315StrictStringBoolFloatReferencePeer\Box315Peer::$v by reference' ? 'E|' : 'BAD|';
}
echo $copy315peer === 'saved' && (array)$box315peer === [] ? 'P|' : 'BAD|';
unset($e);
$box315peer->v = 0.0;
$copy315peer = $box315peer->v;
echo $copy315peer === 0.0 ? 'V|' : 'BAD|';
$copy315peer = 17;
$a315peer =& $box315peer->v;
$b315peer =& $box315peer->v;
echo $a315peer === 0.0 && $b315peer === 0.0 && $copy315peer === 17 ? 'N|' : 'BAD|';
$a315peer = 23;
echo $a315peer === 23.0 && $b315peer === 23.0 ? 'J|' : 'BAD|';
$b315peer = true;
echo $a315peer === true && $b315peer === true ? 'D|' : 'BAD|';
$probe_bool315peer = $box315peer->v;
echo $probe_bool315peer === true && $a315peer === true && $b315peer === true && $copy315peer === 17 ? 'G|' : 'BAD|';
unset($probe_bool315peer);
$a315peer = false;
echo $a315peer === false && $b315peer === false ? 'F|' : 'BAD|';
$a315peer = 'plain';
echo $a315peer === 'plain' && $b315peer === 'plain' ? 'P|' : 'BAD|';
$probe_string315peer = $box315peer->v;
echo $probe_string315peer === 'plain' && $a315peer === 'plain' && $b315peer === 'plain' && $copy315peer === 17 ? 'H|' : 'BAD|';
unset($probe_string315peer);
$a315peer = '12';
echo $a315peer === '12' && $b315peer === '12' ? 'S|' : 'BAD|';
$b315peer = '12.5';
echo $a315peer === '12.5' && $b315peer === '12.5' ? 'L|' : 'BAD|';
$a315peer = '2e0';
echo $a315peer === '2e0' && $b315peer === '2e0' ? 'X|' : 'BAD|';
$b315peer = '';
echo $a315peer === '' && $b315peer === '' ? 'E|' : 'BAD|';
$a315peer = '0';
echo $a315peer === '0' && $b315peer === '0' ? 'Q|' : 'BAD|';
$b315peer = 2;
echo $a315peer === 2.0 && $b315peer === 2.0 ? 'W|' : 'BAD|';
try { $a315peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns315StrictStringBoolFloatReferencePeer\Box315Peer::$v of type string|float|bool' && $a315peer === 2.0 && $b315peer === 2.0 ? 'U|' : 'BAD|';
}
try { $b315peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns315StrictStringBoolFloatReferencePeer\Box315Peer::$v of type string|float|bool' && $a315peer === 2.0 && $b315peer === 2.0 ? 'A|' : 'BAD|';
}
try { $a315peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns315StrictStringBoolFloatReferencePeer\Box315Peer::$v of type string|float|bool' && $a315peer === 2.0 && $b315peer === 2.0 ? 'O|' : 'BAD|';
}
unset($e);
$b315peer = 37;
echo $a315peer === 37.0 && $b315peer === 37.0 && $copy315peer === 17 ? 'K|' : 'BAD|';
unset($box315peer);
$a315peer = 2;
echo $a315peer === 2 && $b315peer === 2 && $copy315peer === 17 ? 'R|' : 'BAD|';
unset($a315peer, $b315peer, $copy315peer);
echo 'Z|';
