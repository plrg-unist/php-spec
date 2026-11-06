<?php
namespace {
    #[Deprecated] const X = [1];
    function notice197() {
        echo 'H|';
        eval('namespace Ns197; const X = [9];');
        $inner = new \Ns197\Box197;
        $GLOBALS['inner197'] = $inner;
        echo $inner->value[0], '|';
        return true;
    }
}
namespace Ns197 {
    class Box197 { public $value = X; }
    set_error_handler('notice197');
    $outer = new Box197;
    $inner = $GLOBALS['inner197'];
    echo $outer->value[0], '|', $inner->value[0], '|';
    $outer->value[0] = 8;
    echo $outer->value[0], '|';
    $fresh = new Box197;
    echo $fresh->value[0], '|';
}
