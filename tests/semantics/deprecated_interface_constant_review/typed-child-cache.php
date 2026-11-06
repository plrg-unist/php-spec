<?php
namespace {
    #[Deprecated]
    const X = [];
    function notice210($level, $message, $file, $line) {
        echo 'H|';
        \define('Ns210Typed\\X', 9);
        echo \Ns210Typed\Child210::VALUE === 9 ? 'N|' : 'BAD|';
        return true;
    }
}
namespace Ns210Typed {
    interface Root210 { public const int VALUE = X; }
    interface Child210 extends Root210 {}
    class Implementer210 implements Child210 {}
    set_error_handler('notice210');
    try { echo Root210::VALUE; }
    catch (\TypeError $error) { echo 'T|'; }
    echo Root210::VALUE === 9 ? 'I|' : 'BAD|';
    echo Child210::VALUE === 9 ? 'J|' : 'BAD|';
    echo Implementer210::VALUE === 9 ? 'K|' : 'BAD|';
    restore_error_handler();
    echo 'Z|';
}
