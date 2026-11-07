<?php
namespace Ns231String;
class Base231 {
    #[\Deprecated] public const A = 7;
}
class Child231 extends Base231 {}
class Other231 {
    #[\Deprecated] public const B = 9;
}
function member231(): string {
    echo 'M|';
    $GLOBALS['class231'] = Other231::class;
    return $GLOBALS['member231'];
}
function notice231($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns231String\\Base231::A is deprecated' ? 'Ha|' :
        ($level === 16384 && $message === 'Constant Ns231String\\Other231::B is deprecated' ? 'Hb|' : 'BAD|');
    $GLOBALS['member231'] = 'B';
    return true;
}
$class231 = Child231::class;
$member231 = 'A';
\set_error_handler('Ns231String\\notice231');
$value231 = $class231::{\Ns231String\member231()};
echo 'O|', $value231, '|';
$value231 = $class231::{\Ns231String\member231()};
echo 'F|', $value231, '|Z|';
