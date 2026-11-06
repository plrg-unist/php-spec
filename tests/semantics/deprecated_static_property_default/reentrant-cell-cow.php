<?php
namespace {
    #[Deprecated] const X = [];
    function notice196() {
        echo 'H|';
        define('Ns196\\X', 9);
        echo \Ns196\Box196::$value, '|';
        \Ns196\Box196::$value = 17;
        return true;
    }
}
namespace Ns196 {
    class Box196 { public static $value = X; }
    set_error_handler('notice196');
    $copy = Box196::$value;
    echo $copy === [] ? 'E|' : 'BAD|';
    $copy[] = 5;
    echo Box196::$value === [] ? 'E|' : 'BAD|';
}
