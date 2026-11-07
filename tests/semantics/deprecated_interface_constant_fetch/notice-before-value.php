<?php
namespace {
    \define('SEED212', 7);
    $nested = false;
    function notice212($level, $message) {
        echo 'C|';
        if (!$GLOBALS['nested']) {
            $GLOBALS['nested'] = true;
            \define('Ns212Order\\SEED212', 9);
            echo 'I|', \Ns212Order\Child212::C, '|';
        }
        return true;
    }
}
namespace Ns212Order {
    interface Base212 { #[\Deprecated] public const C = SEED212; }
    interface Child212 extends Base212 {}
    class Impl212 implements Child212 {}
    \set_error_handler('notice212');
    $outer = Base212::C;
    echo 'O|', $outer, '|';
    $child = Child212::C;
    echo 'J|', $child, '|';
    $impl = Impl212::C;
    echo 'K|', $impl, '|Z|';
}
