<?php
namespace Ns222Member;

interface Base222 {
    #[\Deprecated]
    public const C = [1];
}
interface Child222 extends Base222 {}
class Implementer222 implements Child222 {}
function notice222($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns222Member\\Base222::C is deprecated' ? 'H|' : 'BAD|';
    unset($GLOBALS['member222']);
    return true;
}

$stem222 = 'C';
$member222 = $stem222 . '';
set_error_handler('Ns222Member\\notice222');
$value = Child222::{$member222};
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'M|', $value[0], '|';
$again = Implementer222::C;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
