<?php
namespace {
    #[Deprecated] const X = [];
    function notice200() {
        echo 'H|';
        define('Ns200\\X', 9);
        $inner = Ns200\Other200::make();
        $inner = null;
        echo 'Q|';
    }
}
namespace Ns200 {
    class Root200 {
        function __construct($value = X) {
            echo static::class, '|', ($value === [] ? 'E|' : 'N|');
        }
        function __destruct() { echo 'D|'; }
    }
    class Base200 extends Root200 {
        static function make() { return new static; }
    }
    class First200 extends Base200 {}
    class Other200 extends Base200 {}
    set_error_handler('notice200');
    $outer = First200::make();
    echo 'R|';
    $outer = null;
    echo 'Z|';
}
