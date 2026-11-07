<?php
namespace Ns224Scope;
class Base224 {
    #[\Deprecated] public const A = 7;
    #[\Deprecated] public const B = 8;
    public static function read() {
        global $member224;
        echo 'S|', self::{$member224}, '|L|', static::{$member224}, '|';
    }
}
class Child224 extends Base224 {
    #[\Deprecated] public const B = 9;
}
function notice224($level, $message) {
    echo $message, '|', $level, '|';
    $GLOBALS['member224'] = 'B';
    return true;
}
\set_error_handler('Ns224Scope\\notice224');
$member224 = 'A';
Base224::read();
$member224 = 'A';
Child224::read();
echo 'Z|';
