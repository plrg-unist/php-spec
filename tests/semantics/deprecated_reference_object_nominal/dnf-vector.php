<?php
namespace Ns260NominalVector;
interface I260 {}
interface J260 {}
class LeafBase260 implements I260 {}
class Leaf260 extends LeafBase260 implements J260 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released260vector'] = true;
    }
}
class MiddleBase260 {}
class Middle260 extends MiddleBase260 implements I260 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released260vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields260 {
    public I260&J260 $first;
    public MiddleBase260&I260 $middle;
    public (I260&J260)|Absent260 $last;
    public (I260&J260)|null $nothing;
    public (Missing260&I260)|int $integer;
    public float|(I260&J260) $floating;
    public (I260&J260)|string $request;
    public false|(I260&J260) $onlyFalse;
    public (I260&J260)|true $onlyTrue;
}
class Wide260 extends Fields260 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|';
        echo $this->nothing === null ? 'N|' : 'BAD|';
        echo $this->integer === 17 ? 'I|' : 'BAD|';
        echo $this->floating === 1.5 ? 'F|' : 'BAD|';
        echo $this->request === 'req260' ? 'S|' : 'BAD|';
        echo $this->onlyFalse === false ? 'F|' : 'BAD|';
        echo $this->onlyTrue === true ? 'T|' : 'BAD|';
        $GLOBALS['member260vector'] = 'B';
    }
}
function &selector260() {
    $leaf260 = new Leaf260();
    $receiver260 = new Wide260();
    $receiver260->last = $leaf260;
    $receiver260->first = $leaf260;
    $receiver260->middle = new Middle260();
    $receiver260->nothing = null;
    $receiver260->integer = 17;
    $receiver260->floating = 1.5;
    $suffix260 = '260';
    $receiver260->request = 'req' . $suffix260;
    $receiver260->onlyFalse = false;
    $receiver260->onlyTrue = true;
    echo 'W|';
    return $receiver260;
}
function member260() {
    echo 'M|';
    return $GLOBALS['member260vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns260NominalVector\\Wide260::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member260vector'] = 'A';
    return true;
});
$released260vector = false;
$member260vector = 'A';
echo 'B|', selector260()::{member260()}, '|Z|';
\restore_error_handler();
