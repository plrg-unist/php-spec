<?php
namespace {
    #[Deprecated] const X = [];
    function notice204() { echo 'H|'; \define('Ns204Static\\X', 9); return true; }
}
namespace Ns204Static {
    class Base204 {
        static function load($name, $value = X) {
            echo static::class, '|', $name, '|', ($value === [] ? 'E|' : 'N|');
            $value[] = 7;
        }
    }
    class Child204 extends Base204 {}
    \set_error_handler('notice204');
    \spl_autoload_register([Child204::class, 'LoAd']);
    try { new Missing204; } catch (\Error $error) { echo 'K|'; }
    \spl_autoload_unregister([Child204::class, 'LOAD']);
    \spl_autoload_register('Ns204Static\\Base204::lOaD');
    \spl_autoload_call('Ns204Static\\Second204');
    echo X, '|';
}
