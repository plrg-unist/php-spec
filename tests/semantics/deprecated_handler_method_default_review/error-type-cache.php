<?php
#[Deprecated] const X = [];
class Reject203 {
    function handle($level, $message, $file, $line, int $value = X) {
        echo 'BAD|';
    }
    function __destruct() { echo 'D|'; }
}
$receiver = new Reject203;
$callback = [$receiver, 'handle'];
set_error_handler($callback);
try {
    trigger_error('first', E_USER_WARNING);
} catch (TypeError $error) {
    echo 'T|';
}
try {
    trigger_error('second', E_USER_WARNING);
} catch (TypeError $error) {
    echo 'T|';
}
restore_error_handler();
$callback = null;
$receiver = null;
echo 'Z|';
