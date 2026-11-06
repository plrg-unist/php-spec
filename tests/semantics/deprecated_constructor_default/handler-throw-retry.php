<?php
namespace {
    #[Deprecated] const X = [];
    function notice198() {
        echo 'H|';
        define('Ns198\\X', 9);
        throw new \Exception('before constructor');
    }
}
namespace Ns198 {
    class Box198 {
        function __construct($value = X) { echo 'C|', $value, '|'; }
        function __destruct() { echo 'D|'; }
    }
    set_error_handler('notice198');
    try { $first = new Box198; }
    catch (\Exception $error) { echo 'K|'; }
    $later = new Box198;
    echo 'R|';
    $later = null;
    echo 'Z|';
}
