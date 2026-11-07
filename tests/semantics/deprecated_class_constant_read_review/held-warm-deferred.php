<?php
\define('HELD_DONOR211', 7);
class HeldWarm211 {
    #[\Deprecated]
    public const VALUE = HELD_DONOR211;
}
function notice211($level, $message, $file, $line) {
    echo 'H|';
    return true;
}
set_error_handler('notice211');
echo HeldWarm211::VALUE, '|';
\constant('HeldWarm211::VALUE');
