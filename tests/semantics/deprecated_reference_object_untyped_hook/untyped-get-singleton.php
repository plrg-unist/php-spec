<?php
namespace Ns266UntypedHookSingle;
class LeafBase266 {}
class Leaf266 extends LeafBase266 {
    public function __destruct() {
        echo 'L|';
    }
}
class Selected266 {
    public $edge {
        get => ($GLOBALS['called266single'] = true) ? $this->edge : $this->edge;
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->edge = new Leaf266();
    }
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member266single'] = 'B';
    }
}
function &selector266() {
    $receiver266 = new Selected266();
    echo 'C|';
    return $receiver266;
}
function member266() {
    echo 'M|';
    return $GLOBALS['member266single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns266UntypedHookSingle\\Selected266::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member266single'] = 'A';
    return true;
});
$called266single = false;
$member266single = 'A';
echo 'B|', selector266()::{member266()}, '|', $called266single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
