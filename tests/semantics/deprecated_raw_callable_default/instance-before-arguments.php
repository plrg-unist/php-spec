<?php
namespace {
    #[Deprecated] const X = [];
    function notice207() { echo 'H|'; \define('Ns207Instance\\X', 9); return true; }
    function argument207() {
        echo 'A|';
        $GLOBALS['callback'][1] = 'other';
        $GLOBALS['callback'] = null;
        $GLOBALS['receiver'] = null;
        return 7;
    }
}
namespace Ns207Instance {
    class Receiver207 {
        public $value = 3;
        function run($tag, $value = X) {
            echo 'M|', $this->value, '|', $tag, '|', ($value === [] ? 'E|' : 'N|');
            $value[] = 7;
        }
        function other($tag) { echo 'BAD|'; }
        function __destruct() { echo 'D|'; }
    }
    \set_error_handler('notice207');
    $receiver = new Receiver207;
    $callback = [$receiver, 'rUn'];
    $callback(\argument207());
    echo 'R|';
    $fresh = new Receiver207;
    $fresh->run(8);
    $fresh = null;
    echo 'Z|';
}
