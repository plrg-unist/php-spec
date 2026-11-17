<?php
declare(strict_types=1);
namespace Ns316StrictIntStringBoolFloatShortReferencePeer;
class Box316peer {
    public int|string|bool|float $v = 0 {
        &get =>
            $this->{'v'};
    }
}
$box316peer = new Box316peer();
echo (array)$box316peer === ['v' => 0] ? 'I|' : 'BAD|';
$copy316peer = 'saved';
$copy316peer = $box316peer->v;
echo $copy316peer === 0 ? 'V|' : 'BAD|';
$copy316peer = 17;
$a316peer =& $box316peer->v;
$b316peer =& $box316peer->v;
echo $a316peer === 0 && $b316peer === 0 && $copy316peer === 17 ? 'N|' : 'BAD|';
$a316peer = 23;
echo $a316peer === 23 && $b316peer === 23 ? 'J|' : 'BAD|';
$a316peer = 2.0;
echo $a316peer === 2.0 && $b316peer === 2.0 ? 'D|' : 'BAD|';
$probe_float316peer = $box316peer->v;
echo $probe_float316peer === 2.0 && $a316peer === 2.0 && $b316peer === 2.0 && $copy316peer === 17 ? 'F|' : 'BAD|';
unset($probe_float316peer);
$b316peer = true;
echo $a316peer === true && $b316peer === true ? 'T|' : 'BAD|';
$probe_bool316peer = $box316peer->v;
echo $probe_bool316peer === true && $a316peer === true && $b316peer === true && $copy316peer === 17 ? 'G|' : 'BAD|';
unset($probe_bool316peer);
$a316peer = false;
echo $a316peer === false && $b316peer === false ? 'B|' : 'BAD|';
$a316peer = 'plain';
echo $a316peer === 'plain' && $b316peer === 'plain' ? 'P|' : 'BAD|';
$probe_string316peer = $box316peer->v;
echo $probe_string316peer === 'plain' && $a316peer === 'plain' && $b316peer === 'plain' && $copy316peer === 17 ? 'H|' : 'BAD|';
unset($probe_string316peer);
$a316peer = '12';
echo $a316peer === '12' && $b316peer === '12' ? 'S|' : 'BAD|';
$b316peer = '12.5';
echo $a316peer === '12.5' && $b316peer === '12.5' ? 'L|' : 'BAD|';
$a316peer = '2e0';
echo $a316peer === '2e0' && $b316peer === '2e0' ? 'X|' : 'BAD|';
$b316peer = '';
echo $a316peer === '' && $b316peer === '' ? 'E|' : 'BAD|';
$a316peer = '0';
echo $a316peer === '0' && $b316peer === '0' ? 'Q|' : 'BAD|';
$b316peer = 2.0;
echo $a316peer === 2.0 && $b316peer === 2.0 ? 'W|' : 'BAD|';
try { $a316peer = null; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign null to reference held by property Ns316StrictIntStringBoolFloatShortReferencePeer\Box316peer::$v of type string|int|float|bool' && $a316peer === 2.0 && $b316peer === 2.0 ? 'U|' : 'BAD|';
}
try { $b316peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns316StrictIntStringBoolFloatShortReferencePeer\Box316peer::$v of type string|int|float|bool' && $a316peer === 2.0 && $b316peer === 2.0 ? 'A|' : 'BAD|';
}
try { $a316peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns316StrictIntStringBoolFloatShortReferencePeer\Box316peer::$v of type string|int|float|bool' && $a316peer === 2.0 && $b316peer === 2.0 ? 'O|' : 'BAD|';
}
unset($e);
$b316peer = 37;
echo $a316peer === 37 && $b316peer === 37 && $copy316peer === 17 ? 'K|' : 'BAD|';
unset($box316peer);
$a316peer = null;
echo $a316peer === null && $b316peer === null && $copy316peer === 17 ? 'R|' : 'BAD|';
unset($a316peer, $b316peer, $copy316peer);
echo 'Z|';
