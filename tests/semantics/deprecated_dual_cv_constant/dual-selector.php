<?php
namespace Ns223Select;
class Base223 {
    #[\Deprecated]
    public const A = 7;
}
class Child223 extends Base223 {}
class Other223 {
    #[\Deprecated]
    public const B = 9;
}
function notice223($level, $message) {
    echo $message, '|', $level, '|';
    $GLOBALS['class223'] = 'Ns223Select\\Other223';
    $GLOBALS['member223'] = 'B';
    return true;
}
\set_error_handler('Ns223Select\\notice223');
$class223 = 'nS223SeLeCt\\cHiLd223';
$member223 = 'A';
echo $class223::{$member223}, '|';
echo $class223::{$member223}, '|';
echo Base223::A, '|Z|';
