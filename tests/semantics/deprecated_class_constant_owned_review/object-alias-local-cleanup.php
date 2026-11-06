<?php
class Item194 { public int $value = 3; }
const BASE = new Item194;
#[Deprecated] const X = BASE;
class Local194 {
    public function __destruct() { echo "D|"; BASE->value = 7; }
}
class Cache194 { public const Y = X; }
$alias = BASE;
set_error_handler(function () {
    global $alias;
    $alias = null;
    echo "H|";
    $local = new Local194;
    return true;
});
echo Cache194::Y->value, "|";
echo Cache194::Y === BASE ? "same|" : "BAD|";
