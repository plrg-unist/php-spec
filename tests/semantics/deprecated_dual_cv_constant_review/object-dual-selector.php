<?php
namespace Ns223Dual;

interface Base223 {
    #[\Deprecated]
    public const C = [1];
}
interface Child223 extends Base223 {}
class Selector223 implements Child223 {
    public function __destruct() { echo 'D|'; }
}
function notice223($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns223Dual\\Base223::C is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['selector223'] = null;
    unset($GLOBALS['member223']);
    return true;
}

$selector223 = new Selector223();
$stem223 = 'C';
$member223 = $stem223 . '';
set_error_handler('Ns223Dual\\notice223');
$value = $selector223::{$member223};
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'M|', $value[0], '|';
$again = Selector223::C;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
