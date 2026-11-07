<?php
namespace {
    #[\Deprecated]
    const OWNED_INT215 = [];
}
namespace Ns215Typed {
    class Base215 {
        #[\Deprecated]
        public const int VALUE = OWNED_INT215;
    }
    class Child215 extends Base215 {}
    function notice215($level, $message, $file, $line) {
        if ($message === 'Constant OWNED_INT215 is deprecated') {
            echo 'G|';
            \define('Ns215Typed\\OWNED_INT215', 9);
            echo 'I|', Child215::VALUE, '|';
        } else {
            echo 'C|';
        }
        return true;
    }
    \error_reporting(0);
    \set_error_handler('Ns215Typed\\notice215');
    try {
        echo Base215::VALUE, '|A|';
    } catch (\TypeError $error) {
        echo 'T|';
    }
    echo Child215::VALUE, '|';
    \restore_error_handler();
    echo 'Z|';
}
