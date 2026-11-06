<?php
namespace {
    #[Deprecated] const X = [];
    const Y = [];
    class Drop197 {
        function __destruct() {
            echo 'D|';
            $other = new \Ns197\Other197;
            echo $other->value === [] ? 'O|' : 'BAD|';
        }
    }
    function notice197() {
        echo 'H|';
        eval('namespace Ns197; const X = [9];');
        $inner = new \Ns197\Box197;
        $old = $inner->value[0];
        $old(true);
        $old = null;
        $inner = null;
        return true;
    }
}
namespace Ns197 {
    class Other197 { public $value = Y; }
    class Box197 {
        public $value = [static function ($warm = false) {
            static $held = null;
            if ($warm) { $held = new \Drop197; }
            return 7;
        }, X];
    }
    set_error_handler('notice197');
    $outer = new Box197;
    echo $outer->value[1] === [] ? 'E|' : 'BAD|';
    $new = $outer->value[0];
    echo $new(), '|';
}
