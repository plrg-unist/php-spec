<?php
namespace {
#[Deprecated] const X = [1];
function notice186($level, $message) {
    echo 'H|';
    define('Ns186\X', 9);
    \Ns186\receive186();
    return true;
}
}
namespace Ns186 {
function receive186($value = X) { echo $value === 9 ? 'N|' : 'E|'; }
set_error_handler('notice186');
receive186();
receive186();
}
