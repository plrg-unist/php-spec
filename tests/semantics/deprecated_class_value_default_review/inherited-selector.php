<?php
namespace {
    #[Deprecated]
    const X = [];
}
namespace Ns209Scope {
    class Base209 {
        public static function take($value = X) {
            echo static::class, '|', ($value === [] ? 'E|' : 'BAD|');
            $value[] = 7;
        }
    }
    class Child209 extends Base209 {}
    function notice209($level, $message, $file, $line) {
        echo 'H|';
        \define('Ns209Scope\\X', 9);
        $GLOBALS['selector209'] = null;
        return true;
    }
    $selector209 = 'nS209Scope\\cHiLd209';
    set_error_handler('Ns209Scope\\notice209');
    $selector209::take();
    echo 'R|';
    $selector209 = '\\Ns209Scope\\CHILD209';
    $selector209::take();
    $selector209 = 'Ns209Scope\\BASE209';
    $selector209::take();
    $selector209 = null;
    restore_error_handler();
    echo 'Z|';
}
