<?php
#[Deprecated] const X = [];
class Held193 {
    public function __destruct() { echo "S|"; }
}
class Receiver193 {
    public function run($v = X, $clear = false) {
        static $held = null;
        if ($clear) { $held = null; echo "C|"; return 0; }
        if ($held === null) { $held = new Held193; }
        echo $v === [] ? "E|" : "N|";
        return 7;
    }
    public function __destruct() { echo "R|"; }
}
set_error_handler(function () { echo "H|"; return true; });
$receiver = new Receiver193;
$fn = Closure::fromCallable([$receiver, "run"]);
$receiver = null;
echo $fn(), "|";
$copy = clone $fn;
$fn = null;
echo "A|";
$copy = null;
echo "B|";
$reset = new Receiver193;
$reset->run(null, true);
$reset = null;
echo "D|";
