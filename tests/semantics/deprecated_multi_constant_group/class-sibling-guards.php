<?php
namespace Ns217Class;
\define('SCALAR217', 7);
class Base217 {
    #[\Deprecated]
    public const
        FIRST = \SCALAR217,
        SECOND = 8;
}
class Child217 extends Base217 {}
function notice217($level, $message) {
    if ($message === 'Constant Ns217Class\\Base217::FIRST is deprecated') {
        echo 'H|A|';
        echo 'a|', Child217::FIRST, '|';
        echo 'b|', Child217::SECOND, '|';
    } else { echo 'H|B|'; }
    return true;
}
\error_reporting(0);
\set_error_handler('Ns217Class\\notice217');
echo Base217::FIRST, '|';
echo Child217::SECOND, '|';
echo \constant('Ns217Class\\Child217::FIRST'), '|';
echo 'Z|';
