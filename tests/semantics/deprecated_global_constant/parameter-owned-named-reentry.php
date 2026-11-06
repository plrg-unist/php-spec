<?php
namespace {
#[Deprecated] const X = [];
function notice186($level, $message) { echo 'H|'; define('Ns186\X', 9); \Ns186\receive186(); return true; }
}
namespace Ns186 {
function receive186($value = X, $later = 0) { echo $value === 9 ? 'N|' : 'E|'; echo $later, '|'; }
set_error_handler('notice186');
receive186(later: 5);
receive186(later: 6);
}
