<?php
namespace {
    #[Deprecated] const X = [];
    function notice195() {
        echo 'H|';
        define('Ns195\\X', 9);
        $copy = \Ns195\Cache195::VALUE;
        echo $copy[0], '|';
        eval('const SNAP195 = \\Ns195\\Cache195::VALUE[0];');
        $copy[0] = 17;
        echo \Ns195\Cache195::VALUE[0], '|';
        $copy = null;
        return true;
    }
}
namespace Ns195 {
    class Cache195 { public const VALUE = [X]; }
    set_error_handler('notice195');
    $outer = Cache195::VALUE;
    echo $outer[0] === [] ? 'E|' : 'BAD|';
    echo \SNAP195, '|';
}
