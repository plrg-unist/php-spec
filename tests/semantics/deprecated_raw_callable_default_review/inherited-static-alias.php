<?php
namespace {
    #[Deprecated]
    const X = [];
}
namespace Ns207Scope {
    class Base207 {
        public static function take($value = X) {
            echo static::class, '|', ($value === [] ? 'E|' : 'BAD|');
            $value[] = 1;
        }
        public static function other($value = 0) { echo 'OTHER|'; }
    }
    class Child207 extends Base207 {}
    function notice207($level, $message, $file, $line) {
        echo 'H|';
        \define('Ns207Scope\\X', 9);
        $GLOBALS['callback207'] = 'Ns207Scope\\Child207::other';
        return true;
    }
    $callback207 = 'Ns207Scope\\Child207::tAkE';
    \set_error_handler('Ns207Scope\\notice207');
    $callback207();
    $callback207 = ['Ns207Scope\\Child207', 'TAKE'];
    $callback207();
    $callback207 = ['Ns207Scope\\Base207', 'take'];
    $callback207();
    \restore_error_handler();
    echo 'Z|';
}
