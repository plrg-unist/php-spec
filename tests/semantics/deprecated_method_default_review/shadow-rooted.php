<?php
namespace {
    const DONOR187 = static function() { return 'D'; };
    #[Deprecated] const X = DONOR187;
}
namespace Ns187 {
    class Base187 {
        public static function take($value = X) {
            echo self::class, '/', static::class, ':';
            echo $value === \DONOR187 ? 'D|' : $value . '|';
        }
    }
    class Child187 extends Base187 {}
    set_error_handler(function() {
        echo 'H|'; \define('Ns187\\X', 9); return true;
    });
    Child187::take(); Base187::take(); Child187::take();
}
