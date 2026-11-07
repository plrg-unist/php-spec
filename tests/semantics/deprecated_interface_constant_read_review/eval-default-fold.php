<?php
\define('SEED212', 7);
interface I212 {
    #[\Deprecated]
    public const VALUE = SEED212;
}
interface J212 extends I212 {}
class K212 implements J212 {}
function notice212($level, $message, $file, $line) {
    echo 'H|';
    return true;
}
set_error_handler('notice212');
echo J212::VALUE, '|';
eval('echo K212::VALUE, "|";');
eval('function formal212($value = J212::VALUE) { echo $value, "|"; }');
formal212();
formal212();
restore_error_handler();
echo 'Z|';
