<?php
namespace {
const DONOR = new stdClass();
#[Deprecated] const X = DONOR;
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
echo Y === \DONOR ? 'same|' : 'BAD|';
echo X, '|';
}
