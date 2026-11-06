<?php
#[Deprecated] const X = [];
class Receiver193 {
    public function run($v = X) { echo is_array($v) ? "E|" : "N|"; return 7; }
    public function __destruct() {
        global $other;
        echo "R|";
        echo $other(), "|";
        echo "Z|";
    }
}
class Quiet193 extends Receiver193 {
    public function __destruct() { echo "D|"; }
}
set_error_handler(function () { echo "H|"; return true; });
$receiver = new Receiver193;
$fn = Closure::fromCallable([$receiver, "run"]);
$receiver = null;
$quiet = new Quiet193;
$other = Closure::fromCallable([$quiet, "run"]);
$quiet = null;
echo $fn(), "|";
$fn = null;
$other = null;
