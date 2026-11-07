<?php
namespace Ns224Parent;

class Base224 {
    #[\Deprecated]
    public const A = [1];
}
class Child224 extends Base224 {
    public function read() {
        global $member224;
        return parent::{$member224};
    }
    public function __destruct() { echo 'D|'; }
}
function notice224($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns224Parent\\Base224::A is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member224'] = null;
    $GLOBALS['receiver224'] = null;
    return true;
}

$member224 = 'A';
$receiver224 = new Child224();
set_error_handler('Ns224Parent\\notice224');
$value = $receiver224->read();
echo 'R|', $value[0], '|';
$value[0] = 7;
echo 'M|', $value[0], '|';
$again = Base224::A;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
