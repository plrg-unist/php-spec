<?php
namespace {
    #[\Deprecated] const OWNED216 = [1];
    function notice216($level, $message) {
        $GLOBALS['query'] = 'Ns216Array\\Other216::VALUE';
        if ($message === 'Constant OWNED216 is deprecated') {
            echo 'G|';
            try {
                $inner = \Ns216Array\Child216::VALUE;
                echo 'I|', $inner[0], '|';
            } catch (\Error $error) {
                echo 'E|', $error->getMessage(), '|';
            }
        } else { echo 'C|'; }
        return true;
    }
}
namespace Ns216Array {
    class Base216 { #[\Deprecated] public const VALUE = \OWNED216; }
    class Child216 extends Base216 {}
    class Other216 { public const VALUE = 8; }
    \error_reporting(0);
    \set_error_handler('notice216');
    $query = 'Ns216Array\\Child216::VALUE';
    $value = \constant($query);
    echo 'O|', $value[0], '|R|', \constant($query), '|';
    $value[0] = 7;
    echo 'M|', $value[0], '|';
    $again = \constant('Ns216Array\\Base216::VALUE');
    echo 'W|', $again[0], '|Z|';
}
