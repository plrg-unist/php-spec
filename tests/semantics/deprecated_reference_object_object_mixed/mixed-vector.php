<?php
namespace Ns259ObjectMixedVector;
class LeafBase259 {}
class Leaf259 extends LeafBase259 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released259vector'] = true;
    }
}
class Middle259 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released259vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields259 {
    public object $first;
    public object|int $middle;
    public null|object $last;
    public mixed $nothing;
    public mixed $integer;
    public mixed $floating;
    public mixed $request;
    public mixed $onlyFalse;
    public mixed $onlyTrue;
    public ?object $nullable;
    public bool|float|int|string|null|object $selectedPrim;
}
class Wide259 extends Fields259 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|';
        echo $this->nothing === null ? 'N|' : 'BAD|';
        echo $this->integer === 17 ? 'I|' : 'BAD|';
        echo $this->floating === 1.5 ? 'F|' : 'BAD|';
        echo $this->request === 'req259' ? 'S|' : 'BAD|';
        echo $this->onlyFalse === false ? 'F|' : 'BAD|';
        echo $this->onlyTrue === true ? 'T|' : 'BAD|';
        echo $this->nullable === null ? 'N|' : 'BAD|';
        echo $this->selectedPrim === 23 ? 'U|' : 'BAD|';
        $GLOBALS['member259vector'] = 'B';
    }
}
function &selector259() {
    $leaf259 = new Leaf259();
    $receiver259 = new Wide259();
    $receiver259->last = $leaf259;
    $receiver259->first = $leaf259;
    $receiver259->middle = new Middle259();
    $receiver259->nothing = null;
    $receiver259->integer = 17;
    $receiver259->floating = 1.5;
    $suffix259 = '259';
    $receiver259->request = 'req' . $suffix259;
    $receiver259->onlyFalse = false;
    $receiver259->onlyTrue = true;
    $receiver259->nullable = null;
    $receiver259->selectedPrim = 23;
    echo 'W|';
    return $receiver259;
}
function member259() {
    echo 'M|';
    return $GLOBALS['member259vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns259ObjectMixedVector\\Wide259::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member259vector'] = 'A';
    return true;
});
$released259vector = false;
$member259vector = 'A';
echo 'B|', selector259()::{member259()}, '|Z|';
\restore_error_handler();
