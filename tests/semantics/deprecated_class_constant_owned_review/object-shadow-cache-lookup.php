<?php
namespace {
    class Item194 { public int $value = 3; }
    const BASE = new Item194;
    #[Deprecated] const X = BASE;
    function notice194() { echo "H|"; define('Ns194\\X', 9); return true; }
}
namespace Ns194 {
    class Cache194 { public const Y = X; }
    set_error_handler('notice194');
    $first = Cache194::Y;
    echo $first === \BASE ? "same|" : "BAD|";
    $first->value = 7;
    $first = null;
    echo Cache194::Y->value, "|";
    echo X, "|";
}
