<?php
namespace {
    #[Deprecated] const X = [];
    function invoke207() { global $callback; $callback(); }
    function notice207() {
        echo 'H|';
        \define('Ns207Nested\\X', 9);
        $GLOBALS['callback'] = [\Ns207Nested\Box207::class, 'second'];
        invoke207();
        echo 'Q|';
        $GLOBALS['callback'] = [\Ns207Nested\Box207::class, 'first'];
        return true;
    }
}
namespace Ns207Nested {
    class Box207 {
        static function first($value = X) { echo 'F|', ($value === [] ? 'E|' : 'N|'); }
        static function second($value = X) { echo 'S|', $value, '|'; }
    }
    \set_error_handler('notice207');
    $callback = [Box207::class, 'first'];
    \invoke207();
    $callback = [Box207::class, 'second'];
    \invoke207();
    $callback = [Box207::class, 'first'];
    \invoke207();
    echo 'Z|';
}
