<?php
namespace {
    #[Deprecated] const X = [];
    function notice198() { echo 'H|'; }
}
namespace Ns198 {
    class Box198 {
        function __construct($value = X, $tag = 0) {
            $value[] = $tag;
            echo $value[0], '|';
        }
    }
    set_error_handler('notice198');
    $first = new Box198(tag: 1);
    $first->__construct(tag: 2);
    $second = new Box198(tag: 3);
}
