<?php
interface I212 {
    #[\Deprecated]
    public const VALUE = 7;
}
interface J212 extends I212 {}
class K212 implements J212 {}
function notice212($level, $message, $file, $line) {
    echo 'H|', $message, '|', $line, '|';
    echo $file === __FILE__ ? 'F|' : 'BAD|';
    echo $level, '|';
    return true;
}
set_error_handler('notice212');
echo I212::VALUE, '|';
echo J212::VALUE, '|';
echo K212::VALUE, '|';
restore_error_handler();
echo 'Z|';
