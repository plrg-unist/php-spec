<?php
namespace {
    #[Deprecated] const X = [];
    function argument197() { echo 'A|'; return 5; }
    function notice197() {
        echo 'H|';
        define('Ns197\\X', 9);
        try { $inner = new \Ns197\Box197(0); }
        catch (\TypeError $error) { echo 'T|'; }
        return true;
    }
}
namespace Ns197 {
    class Box197 {
        public array $value = X;
        function __construct($input) { echo 'C|'; }
    }
    set_error_handler('notice197');
    $outer = new Box197(\argument197());
    echo $outer->value === [] ? 'E|' : 'BAD|';
}
