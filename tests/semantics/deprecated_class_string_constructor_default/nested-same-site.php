<?php
namespace {
    #[Deprecated] const X = [];
    function make199() {
        global $selected199;
        return new $selected199;
    }
    function notice199() {
        echo 'H|';
        define('Ns199\\X', 9);
        $GLOBALS['selected199'] = 'Ns199\\Other199';
        $inner = make199();
        $inner = null;
        echo 'Q|';
    }
}
namespace Ns199 {
    class Base199 {
        function __construct($value = X) {
            echo static::class, '|', ($value === [] ? 'E|' : 'N|');
        }
        function __destruct() { echo 'D|'; }
    }
    class First199 extends Base199 {}
    class Other199 extends Base199 {}
    set_error_handler('notice199');
    $selected199 = First199::class;
    $outer = make199();
    echo 'R|';
    $outer = null;
    echo 'Z|';
}
