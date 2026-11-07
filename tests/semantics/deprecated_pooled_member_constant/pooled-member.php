<?php
namespace Ns225Pool;
class Base225 {
    #[\Deprecated] public const VALUE = 7;
    #[\Deprecated] public const OTHER = 9;
}
class Child225 extends Base225 {}
function notice225($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns225Pool\\Base225::VALUE is deprecated' ? 'H|' : 'BAD|';
    echo 'N|', Child225::{('V' . 'ALUE')}, '|';
    return true;
}
\set_error_handler('Ns225Pool\\notice225');
echo 'B|', Child225::{'VALUE'}, '|';
echo 'C|', Child225::{('V' . 'ALUE')}, '|Z|';
