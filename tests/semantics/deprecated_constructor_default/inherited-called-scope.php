<?php
namespace {
    #[Deprecated] const X = [];
    function notice198() { echo 'H|'; }
}
namespace Ns198 {
    class Base198 {
        function __construct($value = X) {
            echo static::class, '|', ($value === [] ? 'E|' : 'N|');
        }
    }
    class Child198 extends Base198 {}
    set_error_handler('notice198');
    $base = new Base198;
    $child = new Child198;
    $child->__construct();
    echo 'Z|';
}
