<?php
namespace Ns258ClassUnionVector;
class LeafBase258 {}
class Leaf258 extends LeafBase258 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released258vector'] = true;
    }
}
class Middle258 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released258vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields258 {
    public Middle258|LeafBase258 $first;
    public LeafBase258|Middle258|int $middle;
    public null|Middle258|LeafBase258 $last;
    public ?LeafBase258 $nothing;
    public LeafBase258|int $integer;
    public float|LeafBase258 $floating;
    public LeafBase258|string $request;
    public LeafBase258|false $onlyFalse;
    public true|LeafBase258 $onlyTrue;
    public LeafBase258|bool $boolean;
    public Unknown258|int $unknown;
}
class Wide258 extends Fields258 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|';
        echo $this->nothing === null ? 'N|' : 'BAD|';
        echo $this->integer === 17 ? 'I|' : 'BAD|';
        echo $this->floating === 1.5 ? 'F|' : 'BAD|';
        echo $this->request === 'req258' ? 'S|' : 'BAD|';
        echo $this->onlyFalse === false ? 'F|' : 'BAD|';
        echo $this->onlyTrue === true ? 'T|' : 'BAD|';
        echo $this->boolean === false ? 'B|' : 'BAD|';
        echo $this->unknown === 23 ? 'U|' : 'BAD|';
        $GLOBALS['member258vector'] = 'B';
    }
}
function &selector258() {
    $leaf258 = new Leaf258();
    $receiver258 = new Wide258();
    $receiver258->last = $leaf258;
    $receiver258->first = $leaf258;
    $receiver258->middle = new Middle258();
    $receiver258->nothing = null;
    $receiver258->integer = 17;
    $receiver258->floating = 1.5;
    $suffix258 = '258';
    $receiver258->request = 'req' . $suffix258;
    $receiver258->onlyFalse = false;
    $receiver258->onlyTrue = true;
    $receiver258->boolean = false;
    $receiver258->unknown = 23;
    echo 'W|';
    return $receiver258;
}
function member258() {
    echo 'M|';
    return $GLOBALS['member258vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns258ClassUnionVector\\Wide258::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member258vector'] = 'A';
    return true;
});
$released258vector = false;
$member258vector = 'A';
echo 'B|', selector258()::{member258()}, '|Z|';
\restore_error_handler();
