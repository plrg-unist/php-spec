<?php
#[Deprecated] const X = [];
class Local202 {
    function __destruct() { echo 'L|'; }
}
function notice202() {
    echo 'H|';
    $local = new Local202;
    return true;
}
class Argument202 {
    public $label = 'A';
    function __destruct() { echo 'G|'; }
}
class Receiver202 {
    function run($argument, $value = X) {
        echo 'M|', $argument->label, '|', ($value === [] ? 'E|' : 'BAD|');
    }
    function __destruct() { echo 'D|'; }
}
function done202() { echo 'Z|'; }
$receiver = new Receiver202;
$argument = new Argument202;
set_error_handler('notice202');
register_shutdown_function([$receiver, 'run'], $argument);
register_shutdown_function('done202');
$receiver = null;
$argument = null;
echo 'R|';
