<?php
namespace {
    #[Deprecated] const X = [];
    function notice210() {
        echo 'H|';
        \define('Ns210Prefix\\X', 9);
        $early = \Ns210Prefix\Child210::C;
        echo $early[0], '|';
        eval('echo "P|"; $v = \Ns210Prefix\Impl210::C; echo $v[0], "|";');
        return true;
    }
}
namespace Ns210Prefix {
    interface Base210 { public const C = [X]; }
    interface Child210 extends Base210 {}
    class Impl210 implements Child210 {}
    \set_error_handler('notice210');
    $late = Base210::C;
    echo ($late[0] === [] ? 'E|' : 'BAD|');
    eval('echo "Q|"; $v = \Ns210Prefix\Child210::C; echo ($v[0] === [] ? "E|" : "BAD|");');
    echo 'Z|';
}
