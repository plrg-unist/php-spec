<?php
namespace {
    #[Deprecated] const X = [];
    function notice205() { echo 'H|'; \define('Ns205Object\\X', 9); return true; }
}
namespace Ns205Object {
    class Receiver205 {
        function run($tag, $value = X) {
            echo $tag, '|', ($value === [] ? 'E|' : 'N|');
            $value[] = 7;
        }
        function other($tag) { echo 'BAD|'; }
        function __destruct() { echo 'D|'; }
    }
    $receiver = new Receiver205;
    $callback = [$receiver, 'rUn'];
    $tag = 7;
    \set_error_handler('notice205');
    \register_tick_function($callback, $tag);
    $tag = 9;
    $callback[1] = 'other';
    declare(ticks=1) { echo 'M|'; }
    \unregister_tick_function([$receiver, 'RUN']);
    $callback = null;
    $receiver = null;
    echo 'R|';
    $fresh = new Receiver205;
    $fresh->run(8);
    $fresh = null;
    echo 'Z|';
}
