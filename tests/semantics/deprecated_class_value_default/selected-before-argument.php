<?php
namespace {
    #[Deprecated] const X = [];
    function notice209() { echo 'H|'; \define('Ns209Argument\\X', 9); return true; }
    function argument209() {
        echo 'A|';
        $GLOBALS['class'] = 'Ns209Argument\\Other209';
        return 7;
    }
}
namespace Ns209Argument {
    class Base209 {
        static function run($tag, $value = X) {
            echo static::class, '|', $tag, '|', ($value === [] ? 'E|' : 'N|');
            $value[] = 7;
        }
    }
    class Child209 extends Base209 {}
    class Other209 {
        static function run($tag, $value = X) { echo 'O|', $tag, '|', $value, '|'; }
    }
    \set_error_handler('notice209');
    $class = 'Ns209Argument\\Child209';
    $class::run(\argument209());
    $class::run(8);
    echo 'Z|';
}
