<?php
namespace {
    #[Deprecated] const X = [];
    function notice196() {
        echo 'H|';
        define('Ns196\\X', 9);
        exit(7);
    }
    function final196() { echo 'S|', \Ns196\Box196::$value, '|'; }
}
namespace Ns196 {
    class Box196 { public static $value = X; }
    register_shutdown_function('final196');
    set_error_handler('notice196');
    $first = Box196::$value;
    echo 'BAD|';
}
