<?php
namespace {
    #[Deprecated] const X = [1];
    function notice197() {
        echo 'H|';
        eval('namespace Ns197; const X = [9];');
        $inner = new \Ns197\Base197;
        echo $inner->slot[0], '|';
        eval('namespace Ns197; class Child197 extends Base197 {}');
        $GLOBALS['during'] = new \Ns197\Child197;
        echo $GLOBALS['during']->slot[0], '|';
        return true;
    }
}
namespace Ns197 {
    class Base197 { public $slot = X; }
    $during = null;
    set_error_handler('notice197');
    $outer = new Base197;
    echo $outer->slot[0], '|';
    $later = new Child197;
    echo $later->slot[0], '|';
    $during->slot[0] = 8;
    echo $during->slot[0], '|', $later->slot[0], '|';
    $fresh = new Child197;
    echo $fresh->slot[0], '|';
    $base = new Base197;
    echo $base->slot[0], '|';
}
