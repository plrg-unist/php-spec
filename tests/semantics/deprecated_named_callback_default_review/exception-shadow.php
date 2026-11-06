<?php
namespace {
    #[Deprecated] const X = [];
    function done206() { echo 'Z|'; }
    class NoticeLocal206 { function __destruct() { echo 'N|'; } }
    class BodyLocal206 { function __destruct() { echo 'L|'; } }
    class Mark206 extends Exception { function __destruct() { echo 'T|'; } }
}
namespace Ns206 {
    function other206($error) { echo 'OTHER|'; }
    function handle206(\Throwable $error, $value = X) {
        echo 'B|', ($value === [] ? 'E|' : 'BAD|'), X, '|';
        $local = new \BodyLocal206;
    }
    function notice206($level, $message, $file, $line) {
        echo 'H|';
        \define('Ns206\\X', 9);
        \set_exception_handler('Ns206\\other206');
        $GLOBALS['callback206'] = null;
        $local = new \NoticeLocal206;
        return true;
    }
    $GLOBALS['callback206'] = 'Ns206\\hAnDlE206';
    \register_shutdown_function('done206');
    \set_error_handler('Ns206\\notice206');
    \set_exception_handler($GLOBALS['callback206']);
    throw new \Mark206('pending');
}
