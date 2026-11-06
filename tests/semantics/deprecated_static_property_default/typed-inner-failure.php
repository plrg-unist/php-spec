<?php
namespace {
    #[Deprecated] const X = [];
    function notice196() {
        echo 'H|';
        define('Ns196\\X', 9);
        try { $inner = \Ns196\Box196::$value; }
        catch (\TypeError $error) { echo 'T|'; }
        return true;
    }
}
namespace Ns196 {
    class Box196 { public static array $value = X; }
    set_error_handler('notice196');
    echo Box196::$value === [] ? 'E|' : 'BAD|';
    echo Box196::$value === [] ? 'E|' : 'BAD|';
}
