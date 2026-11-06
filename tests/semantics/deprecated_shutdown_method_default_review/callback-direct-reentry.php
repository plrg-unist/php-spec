<?php
namespace {
    #[Deprecated] const X = [];
}
namespace Ns202 {
    function notice202() {
        echo 'H|';
        \define('Ns202\\X', 9);
        $GLOBALS['other']->run();
        echo 'Q|';
        return true;
    }
    class Receiver202 {
        function run($value = X) {
            echo 'M|', ($value === [] ? 'E|' : 'N|');
        }
    }
    function finish202() {
        echo 'F|';
        $GLOBALS['other']->run();
        echo 'Z|';
    }
    $receiver = new Receiver202;
    $other = new Receiver202;
    set_error_handler('Ns202\\notice202');
    register_shutdown_function([$receiver, 'run']);
    register_shutdown_function('Ns202\\finish202');
    $receiver = null;
    echo 'R|';
}
