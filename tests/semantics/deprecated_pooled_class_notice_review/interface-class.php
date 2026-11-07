<?php
namespace Ns226ClassPool;

interface Base226 {
    #[\Deprecated]
    public const TREE = [1];
    #[\Deprecated]
    public const OTHER = 9;
}
interface Child226 extends Base226 {}
class Implementer226 implements Child226 {}
function notice226($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns226ClassPool\\Base226::TREE is deprecated' ? 'H|' : 'BAD|';
    return true;
}

set_error_handler('Ns226ClassPool\\notice226');
$value = ('\\nS226cLaSsPoOl\\cHiLd226')::TREE;
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'M|', $value[0], '|';
$again = ('\\Ns226ClassPool\\Implementer' . '226')::{'TR' . 'EE'};
echo 'B|', $again[0], '|';
$last = Base226::TREE;
echo 'L|', $last[0], '|Z|';
restore_error_handler();
