<?php
namespace {
    #[Deprecated] const X = [];
    function notice208() {
        echo 'H|';
        $GLOBALS['receiver'] = null;
        \define('Ns208Instance\\X', 9);
        return true;
    }
    function argument208() { echo 'A|'; return 7; }
}
namespace Ns208Instance {
    class Receiver208 {
        public $value = 3;
        function run($tag, $value = X) {
            echo 'M|', $this->value, '|', $tag, '|', ($value === [] ? 'E|' : 'N|');
            $value[] = 7;
        }
        function __destruct() { echo 'D|'; }
    }
    \set_error_handler('notice208');
    $receiver = null;
    $result = $receiver?->run(\argument208());
    echo ($result === null ? 'N|' : 'BAD|');
    $receiver = new Receiver208;
    $receiver?->run(\argument208());
    echo 'R|';
    $fresh = new Receiver208;
    $fresh->run(8);
    $fresh = null;
    echo 'Z|';
}
