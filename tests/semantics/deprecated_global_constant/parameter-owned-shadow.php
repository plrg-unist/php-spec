<?php
namespace {
const DONOR186 = static function() { return 7; };
#[Deprecated] const X = DONOR186;
function notice186($level, $message) { echo 'H|'; define('Ns186\X', 9); return true; }
}
namespace Ns186 {
function receive186($value = X) { if ($value === \DONOR186) { echo 'D|'; } else { echo $value, '|'; } }
set_error_handler('notice186');
receive186();
receive186();
}
