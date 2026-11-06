<?php
#[Deprecated] const X = [];
class Local203 {
    function __destruct() { echo 'L|'; }
}
function plain203() { echo 'P|'; return true; }
class Receiver203 {
    function handle($level, $message, $file, $line, $value = X) {
        echo 'M|', ($value === [] ? 'E|' : 'BAD|');
        set_error_handler('plain203');
        $GLOBALS['callback'] = null;
        $GLOBALS['receiver'] = null;
        $local = new Local203;
        return true;
    }
    function __destruct() { echo 'D|'; }
}
error_reporting(0);
$receiver = new Receiver203;
$callback = [$receiver, 'handle'];
set_error_handler($callback);
trigger_error('first', E_USER_WARNING);
echo 'R|';
$next = new Receiver203;
$next->handle(0, 'direct', '', 0);
$next = null;
echo 'Z|';
