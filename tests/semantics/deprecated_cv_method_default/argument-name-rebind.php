<?php
namespace {
    #[Deprecated] const X = [];
    function notice201() { echo 'H|'; }
    function move201() {
        $GLOBALS['member201'] = 'bar201';
        echo 'A|';
        return 1;
    }
}
namespace Ns201 {
    class Receiver201 {
        function foo201($value = X, $tag = 0) {
            echo 'F|', ($value === [] ? 'E|' : 'N|'), $tag, '|';
            $value[] = 5;
        }
        function bar201($value = X, $tag = 0) {
            echo 'B|', ($value === [] ? 'E|' : 'N|'), $tag, '|';
        }
    }
    set_error_handler('notice201');
    $receiver201 = new Receiver201;
    $member201 = 'FoO201';
    $receiver201->$member201(tag: move201());
    $receiver201->$member201();
    $member201 = 'FOO201';
    $receiver201->$member201();
}
