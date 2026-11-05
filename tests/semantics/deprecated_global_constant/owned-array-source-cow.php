<?php
#[Deprecated] const X = [1];
function notice185($level, $message) {
    echo 'H|';
    $copy = X;
    $copy[0] = 8;
    echo $copy[0], '|';
    return true;
}
set_error_handler('notice185');
$copy = X;
$copy[0] = 7;
echo $copy[0], '|';
$again = constant('X');
echo $again[0], '|';
