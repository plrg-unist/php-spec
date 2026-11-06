<?php
namespace {
    #[Deprecated] const X = [];
    function notice206() { echo 'H|'; \define('Ns206Tick\\X', 9); return true; }
}
namespace Ns206Tick {
    function run206($tag, $value = X) {
        echo $tag, '|', ($value === [] ? 'E|' : 'N|');
        $value[] = 7;
    }
    \set_error_handler('notice206');
    $callback = 'Ns206Tick\\rUn206';
    $tag = 7;
    \register_tick_function($callback, $tag);
    $callback = 'unknown206';
    $tag = 99;
    declare(ticks=1) { echo 'A|'; }
    \unregister_tick_function('Ns206Tick\\RUN206');
    \register_shutdown_function('Ns206Tick\\run206', 9);
    echo 'R|';
    run206(8);
    echo 'Z|';
}
