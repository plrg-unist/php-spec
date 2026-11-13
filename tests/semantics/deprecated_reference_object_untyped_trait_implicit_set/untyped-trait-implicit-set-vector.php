<?php
namespace Ns273UntypedTraitImplicitSetVector;
class LeafBase273 {}
class Leaf273 extends LeafBase273 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released273vector'] = true;
    }
}
class Middle273 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released273vector'] === false ? 'Q|' : 'BAD|';
    }
}
trait Tag273 {
    public $tag = false {
        set {
            $GLOBALS['called273vector'] = true;
            $this->tag = $value;
        }
    }
}
class Fields273 {
    use Tag273;
    public $first;
    public $middle;
    public $last;
    public function __construct() {
        $leaf273 = new Leaf273();
        $this->last = $leaf273;
        $this->middle = new Middle273();
        $this->first = $leaf273;
    }
}
class Wide273 extends Fields273 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'I|' : 'BAD|';
        $GLOBALS['member273vector'] = 'B';
    }
}
function &selector273() {
    $receiver273 = new Wide273();
    echo 'W|';
    return $receiver273;
}
function member273() {
    echo 'M|';
    return $GLOBALS['member273vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns273UntypedTraitImplicitSetVector\\Wide273::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member273vector'] = 'A';
    return true;
});
$called273vector = false;
$released273vector = false;
$member273vector = 'A';
echo 'B|', selector273()::{member273()}, '|', $called273vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
