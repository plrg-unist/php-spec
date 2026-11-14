<?php
namespace Ns302WeakNullableLiteralShortReference;
class Box302 {
    public ?false $f {
        &get =>
            $this->f;
    }
    public ?true $t {
        &get =>
            $this->t;
    }
    public function __destruct() { echo 'D|'; }
}
$box302 = new Box302();
echo (array)$box302 === [] ? 'I|' : 'BAD|';
$f302 =& $box302->f;
$t302 =& $box302->t;
echo $f302 === null && $t302 === null ? 'N|' : 'BAD|';
$f302 = false;
$t302 = true;
echo $f302 === false && $t302 === true && $box302->f === false && $box302->t === true ? 'G|' : 'BAD|';
$copyf302 = $box302->f;
$copyt302 = $box302->t;
$f302 = null;
$t302 = null;
echo $f302 === null && $t302 === null && $copyf302 === false && $copyt302 === true ? 'Q|' : 'BAD|';
$f302 = false;
$t302 = true;
try { $f302 = 0; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns302WeakNullableLiteralShortReference\Box302::$f of type ?false' ? 'If|' : 'BAD|';
}
try { $t302 = 1; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns302WeakNullableLiteralShortReference\Box302::$t of type ?true' ? 'It|' : 'BAD|';
}
try { $f302 = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns302WeakNullableLiteralShortReference\Box302::$f of type ?false' ? 'Bf|' : 'BAD|';
}
try { $t302 = false; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign false to reference held by property Ns302WeakNullableLiteralShortReference\Box302::$t of type ?true' ? 'Bt|' : 'BAD|';
}
try { $f302 = '0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns302WeakNullableLiteralShortReference\Box302::$f of type ?false' ? 'Sf|' : 'BAD|';
}
try { $t302 = '1'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns302WeakNullableLiteralShortReference\Box302::$t of type ?true' ? 'St|' : 'BAD|';
}
try { $f302 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns302WeakNullableLiteralShortReference\Box302::$f of type ?false' ? 'Af|' : 'BAD|';
}
try { $t302 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns302WeakNullableLiteralShortReference\Box302::$t of type ?true' ? 'At|' : 'BAD|';
}
unset($e);
echo $f302 === false && $t302 === true && $copyf302 === false && $copyt302 === true ? 'K|' : 'BAD|';
unset($box302);
$f302 = [];
$t302 = 'free';
echo $f302 === [] && $t302 === 'free' && $copyf302 === false && $copyt302 === true ? 'R|' : 'BAD|';
unset($f302, $t302, $copyf302, $copyt302);
echo 'Z|';
