<?php
namespace {
    #[Deprecated] const X = [];
    function notice199() { echo 'H|'; }
    function move199() {
        $GLOBALS['selected199'] = 'Ns199\\Other199';
        echo 'A|';
        return 1;
    }
}
namespace Ns199 {
    class Base199 {
        function __construct($value = X, $tag = 0) {
            echo static::class, '|', ($value === [] ? 'E|' : 'N|'), $tag, '|';
        }
    }
    class First199 extends Base199 {}
    class Other199 extends Base199 {}
    set_error_handler('notice199');
    $selected199 = First199::class;
    $first = new $selected199(tag: move199());
    $second = new $selected199;
}
