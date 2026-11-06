<?php
namespace {
    #[Deprecated] const X = [];
    function notice196() {
        echo 'H|';
        define('Ns196\\X', 9);
        throw new \Exception('before bind');
    }
}
namespace Ns196 {
    class Box196 { public static $value = X; }
    set_error_handler('notice196');
    try { $first = Box196::$value; }
    catch (\Exception $error) { echo 'K|'; }
    echo Box196::$value, '|';
}
