<?php
namespace Ns264HookVector;
class LeafBase264 {}
class Leaf264 extends LeafBase264 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released264vector'] = true;
    }
}
class Middle264 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released264vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields264 {
    public LeafBase264 $first {
        get {
            echo 'BADGET|';
            return $this->first;
        }
    }
    public int $tag = 17 {
        set {
            echo 'BADSET|';
            $this->tag = $value;
        }
    }
    public Middle264 $middle;
    public LeafBase264 $last {
        get {
            echo 'BADGET|';
            return $this->last;
        }
    }
    public function __construct() {
        $leaf264 = new Leaf264();
        $this->last = $leaf264;
        $this->middle = new Middle264();
        $this->first = $leaf264;
    }
}
class Wide264 extends Fields264 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member264vector'] = 'B';
    }
}
function &selector264() {
    $receiver264 = new Wide264();
    echo 'W|';
    return $receiver264;
}
function member264() {
    echo 'M|';
    return $GLOBALS['member264vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns264HookVector\\Wide264::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member264vector'] = 'A';
    return true;
});
$released264vector = false;
$member264vector = 'A';
echo 'B|', selector264()::{member264()}, '|Z|';
\restore_error_handler();
