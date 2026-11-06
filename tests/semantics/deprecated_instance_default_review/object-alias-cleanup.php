<?php
namespace {
    class Item197 { public $value = 3; }
    const BASE = new Item197;
    #[Deprecated] const X = BASE;
    class Drop197 {
        function __destruct() { echo 'D|'; $item = BASE; $item->value = 7; }
    }
    function notice197() {
        echo 'H|';
        $GLOBALS['alias'] = null;
        define('Ns197\\X', 9);
        $drop = new Drop197;
        return true;
    }
}
namespace Ns197 {
    class Box197 { public ?\Item197 $slot = X; }
    $alias = \BASE;
    set_error_handler('notice197');
    $first = new Box197;
    $second = new Box197;
    echo $first->slot === \BASE ? 'same|' : 'BAD|';
    echo $second->slot === $first->slot ? 'same|' : 'BAD|';
    echo $first->slot->value, '|';
    $first->slot->value = 8;
    echo $second->slot->value, '|';
    $first->slot = null;
    $second->slot = null;
    $third = new Box197;
    echo $third->slot === \BASE ? 'same|' : 'BAD|';
    echo $third->slot->value, '|';
}
