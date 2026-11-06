<?php
#[Deprecated] const X = [];
class Receiver193 {
    public function run($v = X) { echo is_array($v) ? "E|" : "N|"; return 7; }
    public function __destruct() { echo "R|"; }
}
set_error_handler(function () {
    global $fn;
    $fn = null;
    echo "H|";
    return true;
});
$receiver = new Receiver193;
$fn = $receiver->run(...);
$receiver = null;
echo $fn(), "|";
$receiver = new Receiver193;
$again = $receiver->run(...);
$receiver = null;
echo $again(), "|";
$again = null;
