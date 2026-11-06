<?php
namespace {
    #[Deprecated] const X = [];
    function notice206() { echo 'H|'; \define('Ns206Auto\\X', 9); return true; }
}
namespace Ns206Auto {
    function publish206() { class Wanted206 {} }
    function load206($name, $value = X) {
        echo $name, '|', ($value === [] ? 'E|' : 'N|');
        $value[] = 7;
        if ($name === 'Ns206Auto\\Wanted206') { publish206(); }
    }
    \set_error_handler('notice206');
    $callback = 'Ns206Auto\\lOaD206';
    \spl_autoload_register($callback);
    $callback = 'unknown206';
    $object = new Wanted206;
    echo 'K|';
    \spl_autoload_call('Ns206Auto\\Second206');
    \spl_autoload_unregister('Ns206Auto\\load206');
    load206('direct');
    echo 'Z|';
}
