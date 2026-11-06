<?php
namespace {
    #[Deprecated] const X = [];
    function notice193() {
        global $other;
        echo "H|";
        define('Ns193\\X', 9);
        $other();
        $other = null;
        return true;
    }
}
namespace Ns193 {
    class Receiver193 {
        public function run($v = X) { echo $v === 9 ? "N|" : "E|"; }
        public function __destruct() { echo "R|"; }
    }
    $receiver = new Receiver193;
    $fn = $receiver->run(...);
    $receiver = null;
    $receiver = new Receiver193;
    $other = $receiver->run(...);
    $receiver = null;
    set_error_handler('notice193');
    $fn();
    $fn();
    $fn = null;
}
