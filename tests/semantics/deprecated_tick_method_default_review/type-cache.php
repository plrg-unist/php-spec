<?php
#[Deprecated]
const X = [];

class Reject205 {
    public function tick(int $value = X) { echo 'BAD|'; }
    public function __destruct() { echo 'D|'; }
}
function notice205($number, $message, $file, $line) {
    echo 'H|';
    return true;
}
set_error_handler('notice205');
$GLOBALS['receiver205'] = new Reject205;
register_tick_function([$GLOBALS['receiver205'], 'tick']);
try { declare(ticks=1) { echo 'A|'; } }
catch (TypeError $error) { echo 'T|'; }
try { declare(ticks=1) { echo 'Q|'; } }
catch (TypeError $error) { echo 'T|'; }
unset($error);
unregister_tick_function([$GLOBALS['receiver205'], 'tick']);
$GLOBALS['receiver205'] = null;
echo 'Z|';
