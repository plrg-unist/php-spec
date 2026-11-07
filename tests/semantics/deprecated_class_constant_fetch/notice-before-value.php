<?php
namespace {
    #[Deprecated] const X = [];
    $classCalls = 0;
    function notice211($level, $message) {
        if ($message === 'Constant Ns211Order\\Base211::C is deprecated') {
            echo 'C|';
            if ($GLOBALS['classCalls'] === 0) {
                $GLOBALS['classCalls'] = 1;
                \define('Ns211Order\\X', 9);
                echo 'I|', \Ns211Order\Child211::C, '|';
            }
            return true;
        }
        echo 'G|';
        return true;
    }
}
namespace Ns211Order {
    class Base211 { #[\Deprecated] public const C = X; }
    class Child211 extends Base211 {}
    \set_error_handler('notice211');
    $first = Base211::C;
    echo 'O|', $first, '|';
    $warm = Base211::C;
    echo 'W|', $warm, '|';
    $child = Child211::C;
    echo 'J|', $child, '|';
    echo 'Z|';
}
