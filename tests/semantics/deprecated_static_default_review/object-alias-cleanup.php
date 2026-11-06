<?php
namespace {
    class Item196 { public int $value = 3; }
    const BASE = new Item196;
    #[Deprecated] const X = BASE;
    class Drop196 {
        public function __destruct() {
            echo 'D|';
            $item = BASE;
            $item->value = 7;
        }
    }
    function notice196() {
        global $alias;
        echo 'H|';
        $alias = null;
        $drop = new Drop196;
        return true;
    }
}
namespace Ns196 {
    class Cache196 { public static ?\Item196 $slot = X; }
    $alias = \BASE;
    set_error_handler('notice196');
    $value = Cache196::$slot;
    echo $value->value, '|';
    echo $value === \BASE ? 'same|' : 'BAD|';
    Cache196::$slot = null;
    echo $value->value, '|';
}
