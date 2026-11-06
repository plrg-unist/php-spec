<?php
namespace {
    #[Deprecated] const X = [];
    function invoke209() { global $class; $class::run(); }
    function notice209() {
        echo 'H|';
        \define('Ns209Nested\\X', 9);
        $GLOBALS['class'] = 'Ns209Nested\\Child209';
        invoke209();
        echo 'Q|';
        $GLOBALS['class'] = 'Ns209Nested\\Base209';
        return true;
    }
}
namespace Ns209Nested {
    class Base209 {
        static function run($value = X) { echo 'B|', ($value === [] ? 'E|' : $value . '|'); }
    }
    class Child209 extends Base209 {
        static function run($value = X) { echo 'C|', ($value === [] ? 'E|' : $value . '|'); }
    }
    \set_error_handler('notice209');
    $class = 'Ns209Nested\\Base209';
    \invoke209();
    $class = 'Ns209Nested\\Child209';
    \invoke209();
    $class = 'Ns209Nested\\Base209';
    \invoke209();
    echo 'Z|';
}
