<?php
namespace Ns225Pool;

interface Base225 {
    #[\Deprecated]
    public const TREE = [1];
    #[\Deprecated]
    public const OTHER = 9;
}
interface Child225 extends Base225 {}
class Implementer225 implements Child225 {}
function notice225($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns225Pool\\Base225::TREE is deprecated' ? 'H|' : 'BAD|';
    return true;
}

set_error_handler('Ns225Pool\\notice225');
$value = Child225::{'TR' . 'EE'};
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'M|', $value[0], '|';
$again = Implementer225::{'TREE'};
echo 'B|', $again[0], '|';
$last = Base225::TREE;
echo 'L|', $last[0], '|Z|';
restore_error_handler();
