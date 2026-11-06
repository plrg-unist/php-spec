<?php
namespace {
    #[Deprecated] const X = [];
    function invoke201() {
        global $receiver201, $member201;
        $receiver201->$member201();
    }
    function notice201() {
        echo 'H|';
        define('Ns201\\X', 9);
        $GLOBALS['member201'] = 'bar201';
        invoke201();
        echo 'Q|';
    }
}
namespace Ns201 {
    class Receiver201 {
        function foo201($value = X) {
            echo 'F|', ($value === [] ? 'E|' : 'N|');
        }
        function bar201($value = X) {
            echo 'B|', ($value === [] ? 'E|' : 'N|');
        }
    }
    set_error_handler('notice201');
    $receiver201 = new Receiver201;
    $member201 = 'foo201';
    invoke201();
    echo 'R|';
    $member201 = 'foo201';
    invoke201();
    $member201 = 'bar201';
    invoke201();
}
