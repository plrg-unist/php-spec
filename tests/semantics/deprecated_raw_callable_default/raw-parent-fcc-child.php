<?php
namespace {
    #[Deprecated] const X = [];
    function invoke207() { global $callback; $callback(); }
    function notice207() {
        echo 'H|';
        \define('Ns207Fcc\\X', 9);
        $GLOBALS['callback'] = $GLOBALS['fcc'];
        invoke207();
        echo 'Q|';
        $GLOBALS['callback'] = [\Ns207Fcc\Box207::class, 'run'];
        return true;
    }
}
namespace Ns207Fcc {
    class Box207 {
        static function run($value = X) {
            if ($value === []) { echo 'E|'; } else { echo $value, '|'; }
        }
    }
    $fcc = Box207::run(...);
    $callback = [Box207::class, 'run'];
    \set_error_handler('notice207');
    \invoke207();
    $callback = $fcc;
    \invoke207();
    echo 'Z|';
}
