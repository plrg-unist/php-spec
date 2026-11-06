<?php
namespace {
    #[Deprecated] const X = [];
    function notice194() {
        echo "H|";
        define('Ns194\\X', 9);
        echo \Ns194\Cache194::Y, "|";
        eval('const SNAP194 = \\Ns194\\Cache194::Y;');
        return true;
    }
}
namespace Ns194 {
    class Cache194 { public const Y = X; }
    set_error_handler('notice194');
    echo Cache194::Y === [] ? "E|" : "BAD|";
    echo \SNAP194, "|";
}
