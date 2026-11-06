<?php
namespace {
    #[Deprecated] const X = [];
}
namespace Ns203 {
    class Base203 {
        static function run($level, $message, $file, $line, $value = X) {
            echo static::class, '|', ($value === [] ? 'E|' : 'N|');
            $value[] = 7;
            if (static::class === Child203::class) { \define('Ns203\\X', 9); }
            return true;
        }
    }
    class Child203 extends Base203 {}
    \error_reporting(0);
    \set_error_handler('Ns203\\Child203::rUn');
    \trigger_error('first');
    \set_error_handler([Base203::class, 'RUN']);
    \trigger_error('second');
    echo X, '|';
}
