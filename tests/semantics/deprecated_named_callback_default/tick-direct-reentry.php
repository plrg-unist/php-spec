<?php
namespace {
    #[Deprecated] const X = [];
    function notice206() {
        echo 'H|';
        \define('Ns206Reentry\\X', 9);
        \Ns206Reentry\run206();
        echo 'Q|';
        return true;
    }
}
namespace Ns206Reentry {
    function run206($value = X) {
        if ($value === []) { echo 'E|'; } else { echo $value, '|'; }
    }
    \set_error_handler('notice206');
    \register_tick_function('Ns206Reentry\\run206');
    declare(ticks=1) { echo 'A|'; }
    \unregister_tick_function('Ns206Reentry\\run206');
    run206();
    echo 'Z|';
}
