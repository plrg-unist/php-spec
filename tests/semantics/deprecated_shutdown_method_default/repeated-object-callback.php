<?php
namespace {
    #[Deprecated] const X = [];
    function notice202() { echo 'H|'; }
    function add202($receiver) {
        $callback = [$receiver, 'RuN202'];
        register_shutdown_function($callback);
        $callback[1] = 'other202';
    }
}
namespace Ns202 {
    class Receiver202 {
        function run202($value = X) {
            echo ($value === [] ? 'E|' : 'N|');
            $value[] = 5;
        }
        function other202($value = X) { echo 'BAD|'; }
    }
    set_error_handler('notice202');
    $first = new Receiver202;
    add202($first);
    $first = null;
    $second = new Receiver202;
    add202($second);
    $second = null;
    echo 'M|';
}
