<?php
namespace {
    #[Deprecated] const X = [];
    function notice197() {
        echo 'H|';
        define('Ns197\\X', 9);
        exit(7);
    }
    function final197() {
        echo 'S|';
        $later = new \Ns197\Box197;
        echo $later->value, '|';
    }
}
namespace Ns197 {
    class Box197 {
        public $value = X;
        function __construct() { echo 'C|'; }
    }
    register_shutdown_function('final197');
    set_error_handler('notice197');
    $first = new Box197;
    echo 'BAD|';
}
