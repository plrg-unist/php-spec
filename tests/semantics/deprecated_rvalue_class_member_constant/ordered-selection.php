<?php
namespace Ns230Order;
class Base230 {
    #[\Deprecated] public const A = 7;
}
class Child230 extends Base230 {}
class Other230 {
    #[\Deprecated] public const B = 9;
}
function choose230(): string {
    echo 'C|';
    return $GLOBALS['class230'];
}
function member230(): string {
    echo 'M|';
    $GLOBALS['class230'] = Other230::class;
    return $GLOBALS['member230'];
}
function notice230($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns230Order\\Base230::A is deprecated' ? 'Ha|' :
        ($level === 16384 && $message === 'Constant Ns230Order\\Other230::B is deprecated' ? 'Hb|' : 'BAD|');
    $GLOBALS['member230'] = 'B';
    return true;
}
$class230 = Child230::class;
$member230 = 'A';
\set_error_handler('Ns230Order\\notice230');
$value230 = (\Ns230Order\choose230())::{\Ns230Order\member230()};
echo 'O|', $value230, '|';
$value230 = (\Ns230Order\choose230())::{\Ns230Order\member230()};
echo 'F|', $value230, '|Z|';
