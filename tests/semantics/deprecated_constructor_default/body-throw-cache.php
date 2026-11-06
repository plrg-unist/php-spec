<?php
namespace {
    #[Deprecated] const X = [];
    function notice198() { echo 'H|'; }
}
namespace Ns198 {
    class Box198 {
        function __construct($value = X) {
            echo 'C|';
            throw new \Exception('constructor body');
        }
        function __destruct() { echo 'BAD-D|'; }
    }
    set_error_handler('notice198');
    try { $first = new Box198; }
    catch (\Exception $error) { echo 'K|'; }
    try { $second = new Box198; }
    catch (\Exception $error) { echo 'K|'; }
    echo 'Z|';
}
