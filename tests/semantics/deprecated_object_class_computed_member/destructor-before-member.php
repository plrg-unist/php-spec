<?php
namespace Ns239Object;
class Base239 {
    #[\Deprecated]
    public const A = 7, B = 8;
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member239'] = 'B';
    }
}
class Child239 extends Base239 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
function receiver239() {
    echo 'C|';
    return new Child239();
}
function member239() {
    echo 'M|';
    return $GLOBALS['member239'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns239Object\\Child239::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member239'] = 'A';
    return true;
});
$member239 = 'A';
echo 'B|', receiver239()::{member239()}, '|', $member239, '|Z|';
\restore_error_handler();
