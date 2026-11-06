<?php
#[Deprecated] const X = [];
function notice206() { echo 'H|'; return true; }
function cold206($value = X) {
    echo ($value === [] ? 'E|' : 'N|');
    $value[] = 7;
}
set_error_handler('notice206');
$callback = 'cOlD206';
register_shutdown_function($callback);
$callback = 'unknown206';
register_shutdown_function('COLD206');
echo 'R|';
