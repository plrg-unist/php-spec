<?php
namespace {
    #[Deprecated] const X = [];
    function notice197() {
        echo 'H|';
        define('Ns197\\X', 9);
        throw new \Exception('before template');
    }
}
namespace Ns197 {
    class Box197 {
        public $value = X;
        function __construct() { echo 'C|'; }
    }
    set_error_handler('notice197');
    try { $first = new Box197; }
    catch (\Exception $error) { echo 'K|'; }
    $later = new Box197;
    echo $later->value, '|';
}
