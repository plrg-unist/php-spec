<?php
\define('DONOR211', 7);
class Box211 {
    #[\Deprecated]
    public const VALUE = DONOR211;
}
function notice211($level, $message, $file, $line) {
    echo 'H|';
    return true;
}
set_error_handler('notice211');
echo Box211::VALUE, '|';
eval('echo Box211::VALUE, "|";');
eval('function formal211($value = Box211::VALUE) { echo $value, "|"; }');
formal211();
formal211();
restore_error_handler();
echo 'Z|';
