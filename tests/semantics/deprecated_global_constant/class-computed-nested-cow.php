<?php
namespace {
#[Deprecated] const X = [];
function notice195() {
    echo 'H|'; define('Ns195\\X', 9);
    $copy = \Ns195\Cache195::VALUE; $copy[0][0] = 17;
    echo \Ns195\Cache195::VALUE[0][0] === 9 ? '9|' : 'BAD|';
    return true;
}
}
namespace Ns195 {
class Cache195 { const VALUE = [[X]]; }
set_error_handler('notice195');
$copy = Cache195::VALUE;
echo $copy[0][0] === [] ? 'E|' : 'BAD|';
$copy[0][0] = 18;
echo Cache195::VALUE[0][0] === [] ? 'E|' : 'BAD|';
}
