<?php
class Base211 {
    #[\Deprecated]
    public const VALUE = 7;
}
class Child211 extends Base211 {}
function notice211($level, $message, $file, $line) {
    echo 'H|', $message, '|', $line, '|';
    echo $file === __FILE__ ? 'F|' : 'BAD|';
    echo $level === 8192 ? 'L|' : 'BAD|';
    return true;
}
set_error_handler('notice211');
echo Base211::VALUE, '|';
echo Child211::VALUE, '|';
restore_error_handler();
echo 'Z|';
