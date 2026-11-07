<?php
namespace Ns221Object;

interface Base221 {
    #[\Deprecated]
    public const C = [1];
}
interface Child221 extends Base221 {}
class Selector221 implements Child221 {
    public function __destruct() { echo 'D|'; }
}
function notice221($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns221Object\\Base221::C is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['selector221'] = null;
    return true;
}

$selector221 = new Selector221();
set_error_handler('Ns221Object\\notice221');
$value = $selector221::C;
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'M|', $value[0], '|';
$again = Base221::C;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
