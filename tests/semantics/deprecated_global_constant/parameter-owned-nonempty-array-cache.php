<?php
#[Deprecated] const X = [1];
function receive186($value = X) { echo $value[0], '|'; $value[0] = 7; echo $value[0], '|'; }
set_error_handler(function($level, $message) { echo 'H|'; return true; });
receive186();
receive186();
