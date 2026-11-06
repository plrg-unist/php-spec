<?php
#[Deprecated] const X = [];
function receive186($value = X) { echo isset($value[0]) ? 'BAD|' : 'E|'; $value[] = 7; echo $value[0], '|'; }
set_error_handler(function($level, $message) { echo 'H|'; return true; });
receive186();
receive186();
