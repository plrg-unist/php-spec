<?php
namespace {
    const BASE = static function () {
        echo __CLASS__ === '' ? 'G|' : 'BAD|';
    };
    #[Deprecated]
    const X = BASE;
    function notice210($level, $message, $file, $line) {
        echo 'H|';
        \define('Ns210Closure\\X', 9);
        return true;
    }
}
namespace Ns210Closure {
    interface Root210 { public const VALUE = X; }
    interface Child210 extends Root210 {}
    class Implementer210 implements Child210 {}
    set_error_handler('notice210');
    $first = Child210::VALUE;
    echo $first === \BASE ? 'same|' : 'BAD|';
    $first();
    echo Root210::VALUE === \BASE ? 'I|' : 'BAD|';
    echo Implementer210::VALUE === \BASE ? 'K|' : 'BAD|';
    unset($first);
    restore_error_handler();
    echo 'Z|';
}
