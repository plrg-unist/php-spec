<?php
namespace {
    #[Deprecated] const X = [];
    function notice202() { echo 'H|'; define('Ns202\\X', 9); }
}
namespace Ns202 {
    class Base202 {
        static function run202($tag, $value = X) {
            echo static::class, '|', ($value === [] ? 'E|' : 'N|'), $tag, '|';
        }
    }
    class Child202 extends Base202 {}
    set_error_handler('notice202');
    $tag = 7;
    register_shutdown_function([Child202::class, 'rUn202'], $tag);
    register_shutdown_function('Ns202\\Base202::RUN202', 8);
    $tag = 9;
    echo 'M|';
}
