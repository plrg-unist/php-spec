<?php
namespace {
#[Deprecated] const X = static function() { return 7; };
function notice185($level, $message) {
    echo 'H|';
    define('Ns\X', 9);
    return true;
}
}
namespace Ns {
set_error_handler('notice185');
const Y = X;
restore_error_handler();
$f = Y;
echo $f(), '|', X, '|';
}
