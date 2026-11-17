<?php
declare(strict_types=1);
namespace Ns318StrictBoolIntNullShortReferencePeer;
class Box318peer {
    public bool|int|null $v {
        &get =>
            $this->{'v'};
    }
}
$box318peer = new Box318peer();
echo (array)$box318peer === [] ? 'U|' : 'BAD|';
$copy318peer = 'saved';
$copy318peer = $box318peer->v;
echo $copy318peer === null ? 'V|' : 'BAD|';
echo (array)$box318peer === ['v' => null] ? 'P|' : 'BAD|';
$copy318peer = false;
$a318peer =& $box318peer->v;
$b318peer =& $box318peer->v;
echo $a318peer === null && $b318peer === null && $copy318peer === false ? 'N|' : 'BAD|';
$a318peer = 17;
echo $a318peer === 17 && $b318peer === 17 ? 'J|' : 'BAD|';
$b318peer = true;
echo $a318peer === true && $b318peer === true ? 'T|' : 'BAD|';
$probe_bool318peer = $box318peer->v;
echo $probe_bool318peer === true && $a318peer === true && $b318peer === true && $copy318peer === false ? 'G|' : 'BAD|';
unset($probe_bool318peer);
try { $a318peer = '12'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns318StrictBoolIntNullShortReferencePeer\Box318peer::$v of type int|bool|null' && $a318peer === true && $b318peer === true ? 'S|' : 'BAD|';
}
try { $b318peer = '2e0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns318StrictBoolIntNullShortReferencePeer\Box318peer::$v of type int|bool|null' && $a318peer === true && $b318peer === true ? 'X|' : 'BAD|';
}
try { $a318peer = 'plain'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns318StrictBoolIntNullShortReferencePeer\Box318peer::$v of type int|bool|null' && $a318peer === true && $b318peer === true ? 'Q|' : 'BAD|';
}
try { $b318peer = ''; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns318StrictBoolIntNullShortReferencePeer\Box318peer::$v of type int|bool|null' && $a318peer === true && $b318peer === true ? 'E|' : 'BAD|';
}
try { $a318peer = '0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns318StrictBoolIntNullShortReferencePeer\Box318peer::$v of type int|bool|null' && $a318peer === true && $b318peer === true ? 'C|' : 'BAD|';
}
try { $b318peer = 7.0; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign float to reference held by property Ns318StrictBoolIntNullShortReferencePeer\Box318peer::$v of type int|bool|null' && $a318peer === true && $b318peer === true ? 'F|' : 'BAD|';
}
$a318peer = false;
echo $a318peer === false && $b318peer === false ? 'B|' : 'BAD|';
$a318peer = null;
echo $a318peer === null && $b318peer === null ? 'L|' : 'BAD|';
$probe_null318peer = $box318peer->v;
echo $probe_null318peer === null && $a318peer === null && $b318peer === null && $copy318peer === false ? 'H|' : 'BAD|';
unset($probe_null318peer);
try { $b318peer = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns318StrictBoolIntNullShortReferencePeer\Box318peer::$v of type int|bool|null' && $a318peer === null && $b318peer === null ? 'A|' : 'BAD|';
}
try { $a318peer = new \stdClass(); } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign stdClass to reference held by property Ns318StrictBoolIntNullShortReferencePeer\Box318peer::$v of type int|bool|null' && $a318peer === null && $b318peer === null ? 'O|' : 'BAD|';
}
unset($e);
$b318peer = 37;
echo $a318peer === 37 && $b318peer === 37 && $copy318peer === false ? 'K|' : 'BAD|';
unset($box318peer);
$a318peer = 'free';
echo $a318peer === 'free' && $b318peer === 'free' && $copy318peer === false ? 'R|' : 'BAD|';
unset($a318peer, $b318peer, $copy318peer);
echo 'Z|';
