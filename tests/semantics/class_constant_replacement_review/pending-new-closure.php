<?php
namespace {
    #[Deprecated] const X = [];
    class Drop195 {
        public function __destruct() {
            global $phase;
            echo 'D|';
            $phase = 7;
            $during = \Ns195\Aux195::VALUE;
            echo $during[0], '|';
        }
    }
    function notice195() {
        echo 'H|';
        define('Ns195\\X', 9);
        $inner = \Ns195\Cache195::VALUE;
        $old = $inner[0];
        $old(true);
        $old = null;
        $inner = null;
        return true;
    }
}
namespace Ns195 {
    class Aux195 { public const VALUE = [4]; }
    class Cache195 {
        public const VALUE = [static function ($warm = false) {
            static $held = null;
            if ($warm) { $held = new \Drop195; }
            return 7;
        }, X];
    }
    $phase = 0;
    set_error_handler('notice195');
    $outer = Cache195::VALUE;
    echo $outer[1] === [] ? 'E|' : 'BAD|';
    $new = $outer[0];
    echo $new(), '|', $phase, '|';
}
