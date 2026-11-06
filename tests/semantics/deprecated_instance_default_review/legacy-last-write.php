<?php
namespace {
    #[Deprecated] const X = 9;
    function notice197() {
        echo 'H|';
        eval('namespace Ns197; const X = [1];');
        $GLOBALS['kept'] = new \Ns197\Box197;
        echo $GLOBALS['kept']->slot[0], '|';
        return true;
    }
}
namespace Ns197 {
    class Box197 { public $slot = X; }
    $kept = null;
    set_error_handler('notice197');
    $outer = new Box197;
    echo $outer->slot, '|', $kept->slot[0], '|';
    eval('namespace Ns197; class Child197 extends Box197 {}');
    $child = new Child197;
    echo $child->slot, '|';
}
