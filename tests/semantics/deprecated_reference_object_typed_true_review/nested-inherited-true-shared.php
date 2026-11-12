<?php
namespace Ns253TypedTrue;
class Leaf253 {
    public function __destruct() {
        echo 'L|';
    }
}
class Base253 {
    public true $tag;
}
class Middle253 extends Base253 {
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag === true ? 'T|' : 'BAD|';
    }
}
class Root253 {
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root253::A, '|';
        $GLOBALS['member253peer'] = 'B';
    }
}
function &selector253() {
    $middle253 = new Middle253();
    $middle253->tag = true;
    $middle253->edge = $GLOBALS['outside253peer'];
    $receiver253 = new Root253();
    $receiver253->middle = $middle253;
    $receiver253->tail = $GLOBALS['outside253peer'];
    echo 'C|';
    return $receiver253;
}
function member253() {
    echo 'M|';
    return $GLOBALS['member253peer'];
}
function notice253($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns253TypedTrue\\Root253::A is deprecated' || $message === 'Constant Ns253TypedTrue\\Root253::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member253peer'] = 'A';
    return true;
}
$outside253peer = new Leaf253();
$member253peer = 'A';
\set_error_handler('Ns253TypedTrue\\notice253');
echo 'B|', selector253()::{member253()}, '|Z|';
unset($outside253peer);
echo 'E|';
\restore_error_handler();
