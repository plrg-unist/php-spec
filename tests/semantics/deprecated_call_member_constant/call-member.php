<?php
namespace Ns227Call;
class Base227 {
    #[\Deprecated] public const A = 7;
    #[\Deprecated] public const B = 9;
}
function member227() {
    echo 'M|';
    return $GLOBALS['return227'];
}
function notice227($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns227Call\\Base227::A is deprecated' || $message === 'Constant Ns227Call\\Base227::B is deprecated') ? 'H|' : 'BAD|';
    echo 'N|', Base227::{\Ns227Call\member227()}, '|';
    $GLOBALS['return227'] = 'B';
    return true;
}
$return227 = 'A';
\set_error_handler('Ns227Call\\notice227');
echo 'O|', Base227::{\Ns227Call\member227()}, '|';
echo 'F|', Base227::{\Ns227Call\member227()}, '|Z|';
