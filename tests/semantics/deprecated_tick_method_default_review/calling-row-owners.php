<?php
#[Deprecated]
const X = [];

class Payload205 {
    public $value = 7;
    public function __destruct() { echo 'P|'; }
}
class Local205 {
    public function __destruct() { echo 'L|'; }
}
class Receiver205 {
    public function tick($payload, $value = X) {
        echo 'B|', $payload->value, '|', ($value === [] ? 'E|' : 'BAD|');
        $GLOBALS['saved205'] = $this;
        $local = new Local205;
    }
    public function __destruct() { echo 'D|'; }
}
function notice205($number, $message, $file, $line) {
    echo 'H|';
    try { unregister_tick_function($GLOBALS['callback205']); }
    catch (Error $error) { echo 'K|'; }
    $GLOBALS['callback205'] = null;
    $GLOBALS['receiver205'] = null;
    $GLOBALS['payload205'] = null;
    echo 'W|';
    return true;
}
set_error_handler('notice205');
$GLOBALS['receiver205'] = new Receiver205;
$GLOBALS['payload205'] = new Payload205;
$GLOBALS['callback205'] = [$GLOBALS['receiver205'], 'tick'];
register_tick_function($GLOBALS['callback205'], $GLOBALS['payload205']);
declare(ticks=1) { echo 'A|'; }
echo 'R|';
unregister_tick_function([$GLOBALS['saved205'], 'tick']);
$GLOBALS['saved205'] = null;
echo 'Z|';
