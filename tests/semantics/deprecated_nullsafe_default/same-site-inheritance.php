<?php
namespace {
    #[Deprecated] const X = [];
    function invoke208() { global $receiver; $receiver?->run(); }
    function notice208() {
        echo 'H|';
        \define('Ns208Nested\\X', 9);
        $GLOBALS['receiver'] = new \Ns208Nested\Child208;
        invoke208();
        echo 'Q|';
        $GLOBALS['receiver'] = $GLOBALS['base'];
        return true;
    }
}
namespace Ns208Nested {
    class Base208 {
        function run($value = X) { echo 'B|', ($value === [] ? 'E|' : $value . '|'); }
    }
    class Child208 extends Base208 {
        function run($value = X) { echo 'C|', ($value === [] ? 'E|' : $value . '|'); }
    }
    \set_error_handler('notice208');
    $base = new Base208;
    $receiver = $base;
    \invoke208();
    $receiver = new Child208;
    \invoke208();
    $receiver = $base;
    \invoke208();
    echo 'Z|';
}
