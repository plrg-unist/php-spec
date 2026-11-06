<?php
namespace {
    #[Deprecated] const X = [];
    function notice210() {
        echo 'H|';
        \define('Ns210Cache\\X', 9);
        $inner = \Ns210Cache\Child210::C;
        echo $inner[0], '|';
        return true;
    }
}
namespace Ns210Cache {
    interface Base210 { public const C = [X]; }
    interface Child210 extends Base210 {}
    class Impl210 implements Child210 {}
    \set_error_handler('notice210');
    $outer = Base210::C;
    echo ($outer[0] === [] ? 'E|' : 'BAD|');
    $viaChild = Child210::C;
    $viaImpl = Impl210::C;
    echo ($viaChild === $outer && $viaImpl === $outer ? 'same|' : 'BAD|');
    $viaImpl[0][] = 7;
    echo (Base210::C[0] === [] ? 'E|' : 'BAD|');
    echo 'Z|';
}
