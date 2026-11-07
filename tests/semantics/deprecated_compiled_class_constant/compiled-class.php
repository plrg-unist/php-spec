<?php
namespace Ns226Pool;
class Base226 {
    #[\Deprecated] public const VALUE = 7;
    #[\Deprecated] public const OTHER = 8;
}
class Child226 extends Base226 {}
class Other226 {
    #[\Deprecated] public const VALUE = 9;
}
function notice226($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns226Pool\\Base226::VALUE is deprecated' ? 'H|' : 'BAD|';
    echo 'N|', ('Ns226Pool\\Child226')::VALUE, '|';
    return true;
}
\set_error_handler('Ns226Pool\\notice226');
echo 'B|', ('Ns226Pool\\Child226')::VALUE, '|';
echo 'C|', ('Ns226Pool' . '\\Child226')::{('V' . 'ALUE')}, '|Z|';
