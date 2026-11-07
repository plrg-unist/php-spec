<?php
namespace {
    #[\Deprecated] const X = [];
    function notice215($level, $message) {
        if ($message === 'Constant X is deprecated') {
            echo 'G|';
            \define('Ns215Computed\\X', 9);
            $inner = \Ns215Computed\Child215::C;
            echo 'I|', $inner[0], '|';
        } else { echo 'C|'; }
        return true;
    }
}
namespace Ns215Computed {
    class Base215 { #[\Deprecated] public const C = [X]; }
    class Child215 extends Base215 {}
    \error_reporting(0);
    \set_error_handler('notice215');
    $value = Base215::C;
    echo 'O|';
    if ($value[0] === []) { echo 'E|'; } else { echo 'BAD|'; }
    $again = Child215::C;
    if ($again === $value) { echo 'same|'; } else { echo 'BAD|'; }
    $value[0][] = 7;
    echo $value[0][0], '|';
    $last = Base215::C;
    if ($last[0] === []) { echo 'E|Z|'; } else { echo 'BAD|'; }
}
