<?php
namespace Ns245ScalarRetarget;
class Selected245 {
    public $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === true ? 'T|' : 'BAD|';
        $inner245 = Selected245::B;
        echo $inner245, '|';
    }
}
class Other245 {
    public const B = 80;
}
function &selector245() {
    global $selector245peer;
    echo 'C|';
    return $selector245peer;
}
function member245() {
    echo 'M|';
    return $GLOBALS['member245peer'];
}
function notice245($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns245ScalarRetarget\\Selected245::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member245peer'] = 'A';
    $GLOBALS['selector245peer'] = Other245::class;
    echo 'H2|';
    return true;
}
$selector245peer = new Selected245();
$selector245peer->tag = true;
$member245peer = 'B';
\set_error_handler('Ns245ScalarRetarget\\notice245');
echo 'B|';
$value245peer = selector245()::{member245()};
echo 'R|', $value245peer, '|W|', $selector245peer::B, '|Z|';
\restore_error_handler();
