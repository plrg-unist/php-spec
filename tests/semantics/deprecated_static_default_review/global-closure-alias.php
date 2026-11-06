<?php
namespace {
    const BASE = static function () {
        echo __CLASS__ === '' ? 'G|' : 'BAD|';
    };
    #[Deprecated] const X = BASE;
    function notice196() {
        echo 'H|';
        define('Ns196\\X', 9);
        return true;
    }
}
namespace Ns196 {
    class Cache196 { public static $slot = X; }
    set_error_handler('notice196');
    $function = Cache196::$slot;
    $function();
    echo $function === \BASE ? 'same|' : 'BAD|';
    echo X, '|';
}
