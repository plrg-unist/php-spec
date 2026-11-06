<?php
#[Deprecated]
const X = [];
function reject206($level, $message, $file, $line, int $value = X) {
    echo 'BAD|';
}
function other206() { echo 'OTHER|'; }
$handler = 'rEjEcT206';
set_error_handler($handler);
$handler = 'other206';
try { trigger_error('first', E_USER_WARNING); }
catch (TypeError $error) { echo 'T|'; }
try { trigger_error('second', E_USER_WARNING); }
catch (TypeError $error) { echo 'T|'; }
restore_error_handler();
unset($error);
echo 'Z|';
