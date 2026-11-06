<?php
namespace {
    #[Deprecated] const X = [1];
    function notice196() {
        global $alias;
        echo 'H|';
        eval('namespace Ns196; const X = [9];');
        $alias =& \Ns196\Cache196::$slot;
        echo $alias[0], '|';
        return true;
    }
}
namespace Ns196 {
    class Cache196 { public static array $slot = X; }
    $alias = null;
    set_error_handler('notice196');
    echo Cache196::$slot[0], '|', $alias[0], '|';
    try { $alias = 'free'; echo 'BAD|'; }
    catch (\TypeError $error) { echo 'T|'; }
    $alias = [8];
    echo $alias[0], '|', Cache196::$slot[0], '|';
}
