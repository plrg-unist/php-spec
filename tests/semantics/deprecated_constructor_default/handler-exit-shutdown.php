<?php
namespace {
    #[Deprecated] const X = [];
    function notice198() {
        echo 'H|';
        define('Ns198\\X', 9);
        exit(7);
    }
    function final198() {
        echo 'S|';
        $later = new \Ns198\Box198;
        $later = null;
        echo 'Z|';
    }
}
namespace Ns198 {
    class Box198 {
        function __construct($value = X) { echo 'C|', $value, '|'; }
        function __destruct() { echo 'D|'; }
    }
    register_shutdown_function('final198');
    set_error_handler('notice198');
    $first = new Box198;
    echo 'BAD|';
}
