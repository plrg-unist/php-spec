<?php
namespace Ns265ShortSetVector;
class LeafBase265 {}
class Leaf265 extends LeafBase265 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released265vector'] = true;
    }
}
class Middle265 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released265vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields265 {
    public LeafBase265 $first;
    public int $tag = 17 {
        set => ($GLOBALS['called265vector'] = true) ? 99 : $value;
    }
    public Middle265 $middle;
    public LeafBase265 $last;
    public function __construct() {
        $leaf265 = new Leaf265();
        $this->last = $leaf265;
        $this->middle = new Middle265();
        $this->first = $leaf265;
    }
}
class Wide265 extends Fields265 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member265vector'] = 'B';
    }
}
function &selector265() {
    $receiver265 = new Wide265();
    echo 'W|';
    return $receiver265;
}
function member265() {
    echo 'M|';
    return $GLOBALS['member265vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns265ShortSetVector\\Wide265::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member265vector'] = 'A';
    return true;
});
$called265vector = false;
$released265vector = false;
$member265vector = 'A';
echo 'B|', selector265()::{member265()}, '|', $called265vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
