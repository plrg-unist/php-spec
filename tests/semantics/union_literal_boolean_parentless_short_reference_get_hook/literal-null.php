<?php
namespace Ns303WeakLiteralNullShortReference;
class Box303 {
    public false|null $f {
        &get =>
            $this->f;
    }
    public true|null $t {
        &get =>
            $this->t;
    }
    public function __destruct() { echo 'D|'; }
}
$box303 = new Box303();
echo (array)$box303 === [] ? 'I|' : 'BAD|';
$f303 =& $box303->f;
$t303 =& $box303->t;
echo $f303 === null && $t303 === null ? 'N|' : 'BAD|';
$f303 = false;
$t303 = true;
echo $f303 === false && $t303 === true && $box303->f === false && $box303->t === true ? 'G|' : 'BAD|';
$copyf303 = $box303->f;
$copyt303 = $box303->t;
$f303 = null;
$t303 = null;
echo $f303 === null && $t303 === null && $copyf303 === false && $copyt303 === true ? 'Q|' : 'BAD|';
$f303 = false;
$t303 = true;
try { $f303 = 0; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns303WeakLiteralNullShortReference\Box303::$f of type ?false' ? 'If|' : 'BAD|';
}
try { $t303 = 1; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns303WeakLiteralNullShortReference\Box303::$t of type ?true' ? 'It|' : 'BAD|';
}
try { $f303 = true; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign true to reference held by property Ns303WeakLiteralNullShortReference\Box303::$f of type ?false' ? 'Bf|' : 'BAD|';
}
try { $t303 = false; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign false to reference held by property Ns303WeakLiteralNullShortReference\Box303::$t of type ?true' ? 'Bt|' : 'BAD|';
}
try { $f303 = '0'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns303WeakLiteralNullShortReference\Box303::$f of type ?false' ? 'Sf|' : 'BAD|';
}
try { $t303 = '1'; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign string to reference held by property Ns303WeakLiteralNullShortReference\Box303::$t of type ?true' ? 'St|' : 'BAD|';
}
try { $f303 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns303WeakLiteralNullShortReference\Box303::$f of type ?false' ? 'Af|' : 'BAD|';
}
try { $t303 = []; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign array to reference held by property Ns303WeakLiteralNullShortReference\Box303::$t of type ?true' ? 'At|' : 'BAD|';
}
unset($e);
echo $f303 === false && $t303 === true && $copyf303 === false && $copyt303 === true ? 'K|' : 'BAD|';
unset($box303);
$f303 = [];
$t303 = 'free';
echo $f303 === [] && $t303 === 'free' && $copyf303 === false && $copyt303 === true ? 'R|' : 'BAD|';
unset($f303, $t303, $copyf303, $copyt303);
echo 'Z|';
