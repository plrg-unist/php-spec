<?php
namespace {
    #[Deprecated] const X = [];
    function notice198() { echo 'H|'; }
    function argument198() { echo 'A|'; return 0; }
}
namespace Ns198 {
    class Typed198 {
        function __construct(string $value = X, $tag = 0) { echo 'BAD|'; }
        function __destruct() { echo 'BAD-D|'; }
    }
    set_error_handler('notice198');
    try { $first = new Typed198(tag: argument198()); }
    catch (\TypeError $error) { echo 'T|'; }
    try { $second = new Typed198(tag: argument198()); }
    catch (\TypeError $error) { echo 'T|'; }
    echo 'Z|';
}
