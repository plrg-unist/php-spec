<?php
#[Deprecated] const X = [];
class Receiver193 {
    private function hidden($v = X) { echo is_array($v) ? "E|" : "N|"; return 7; }
    public function make() { return $this->hidden(...); }
    public function __destruct() { echo "R|"; }
}
set_error_handler(function () { echo "H|"; return true; });
$receiver = new Receiver193;
$fn = $receiver->make();
$receiver = null;
echo $fn(), "|";
$fn = null;
