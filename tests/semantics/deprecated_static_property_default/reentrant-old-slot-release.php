<?php
namespace {
    #[Deprecated] const X = [];
    const Y = [];
    class Drop196 {
        function __destruct() {
            echo 'D|';
            $other = \Ns196\Other196::$value;
            echo $other === [] ? 'O|' : 'BAD|';
        }
    }
    function notice196() {
        echo 'H|';
        define('Ns196\\X', 9);
        $inner = \Ns196\Box196::$value;
        \Ns196\Box196::$value = new Drop196;
        return true;
    }
}
namespace Ns196 {
    class Other196 { public static $value = Y; }
    class Box196 { public static $value = X; }
    set_error_handler('notice196');
    echo Box196::$value === [] ? 'E|' : 'BAD|';
}
