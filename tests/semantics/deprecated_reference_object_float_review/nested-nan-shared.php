<?php
namespace Ns246NestedFloat;
class Leaf246 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle246 {
    public $tag;
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag !== $this->tag ? 'N|' : 'BAD|';
    }
}
class Root246 {
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root246::A, '|';
        $GLOBALS['member246peer'] = 'B';
    }
}
function &selector246() {
    $middle246 = new Middle246();
    $middle246->tag = NAN;
    $middle246->edge = $GLOBALS['outside246peer'];
    $receiver246 = new Root246();
    $receiver246->middle = $middle246;
    $receiver246->tail = $GLOBALS['outside246peer'];
    echo 'C|';
    return $receiver246;
}
function member246() {
    echo 'M|';
    return $GLOBALS['member246peer'];
}
function notice246($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns246NestedFloat\\Root246::A is deprecated' || $message === 'Constant Ns246NestedFloat\\Root246::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member246peer'] = 'A';
    return true;
}
$outside246peer = new Leaf246();
$member246peer = 'A';
\set_error_handler('Ns246NestedFloat\\notice246');
echo 'B|', selector246()::{member246()}, '|Z|';
unset($outside246peer);
echo 'E|';
\restore_error_handler();
