<?php
namespace {
    #[Deprecated] const X = [];
    function notice205() { echo 'H|'; \define('Ns205Static\\X', 9); return true; }
}
namespace Ns205Static {
    class Base205 {
        static function run($value = X) {
            echo static::class, '|', ($value === [] ? 'E|' : 'N|');
            $value[] = 7;
        }
    }
    class Child205 extends Base205 {}
    \set_error_handler('notice205');
    \register_tick_function([Child205::class, 'rUn']);
    declare(ticks=1) { echo 'A|'; }
    \unregister_tick_function([Child205::class, 'RUN']);
    \register_tick_function('Ns205Static\\Base205::rUN');
    declare(ticks=1) { echo 'B|'; }
    \unregister_tick_function('Ns205Static\\Base205::run');
    echo X, '|';
}
