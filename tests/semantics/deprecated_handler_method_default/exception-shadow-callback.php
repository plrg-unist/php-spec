<?php
namespace {
    #[Deprecated] const X = [];
    class Local203 {
        function __destruct() { echo 'L|'; }
    }
    function notice203() {
        echo 'H|';
        \define('Ns203Exception\\X', 9);
        $GLOBALS['receiver'] = null;
        $local = new Local203;
        return true;
    }
    function done203() { echo 'Z|'; }
}
namespace Ns203Exception {
    class Receiver203 {
        function run($exception, $value = X) {
            echo 'M|', ($value === [] ? 'E|' : 'N|'), X, '|';
        }
        function __destruct() { echo 'R|'; }
    }
    $GLOBALS['receiver'] = new Receiver203;
    \set_error_handler('notice203');
    \set_exception_handler([$GLOBALS['receiver'], 'rUn']);
    \register_shutdown_function('done203');
    echo 'F|';
    throw new \Exception('original');
}
