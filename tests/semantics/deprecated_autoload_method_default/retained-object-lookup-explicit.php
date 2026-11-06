<?php
namespace {
    #[Deprecated] const X = [];
    function notice204() { echo 'H|'; \define('Ns204Object\\X', 9); return true; }
}
namespace Ns204Object {
    class Loader204 {
        function load($name, $value = X) {
            echo 'M|', $name, '|', ($value === [] ? 'E|' : 'N|');
            $value[] = 7;
        }
        function __destruct() { echo 'D|'; }
    }
    $loader = new Loader204;
    $callback = [$loader, 'LoAd'];
    \set_error_handler('notice204');
    \spl_autoload_register($callback);
    try { new Missing204; } catch (\Error $error) { echo 'K|'; }
    \spl_autoload_call('Ns204Object\\Second204');
    \spl_autoload_unregister($callback);
    $callback = null;
    $loader = null;
    echo 'R|';
    $fresh = new Loader204;
    $fresh->load('direct');
    $fresh = null;
    echo 'Z|';
}
