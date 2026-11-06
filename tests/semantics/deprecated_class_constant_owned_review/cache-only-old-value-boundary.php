<?php
namespace {
    #[Deprecated] const X = [];
    function notice194() {
        echo "H|";
        define('Ns194\\X', 9);
        $inner = \Ns194\Cache194::Y;
        echo $inner[0], "|";
        return true;
    }
}
namespace Ns194 {
    class Cache194 { public const Y = [X]; }
    set_error_handler('notice194');
    $outer = Cache194::Y;
    echo $outer[0] === [] ? "E|" : "BAD|";
}
