<?php
namespace {
class Item194 { public int $value = 7; }
const BASE = new Item194;
#[Deprecated] const X = [];
function notice194() {
    echo 'H|';
    eval('namespace Ns194; const X = \\BASE;');
    $child = \Ns194\Cache194::VALUE;
    echo $child === BASE ? 'same|' : 'BAD|';
    return true;
}
}
namespace Ns194 {
class Cache194 { const VALUE = X; }
set_error_handler('notice194');
echo Cache194::VALUE === [] ? 'E|' : 'BAD|';
echo Cache194::VALUE === [] ? 'E|' : 'BAD|';
}
