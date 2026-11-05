<?php
const BASE = new stdClass();
$base = BASE;
$base->value = 1;
#[Deprecated] const X = [BASE];
class Retval185 {
    function __destruct() {
        echo 'R|';
        $inner = X;
        $leaf = $inner[0];
        $leaf->value = $leaf->value + 1;
    }
}
set_error_handler(function($level, $message) { echo 'H|'; return new Retval185(); });
$first = X;
echo $first[0]->value, '|';
$second = constant('X');
echo $second[0]->value, '|', $first[0] === $second[0] ? 'same|' : 'BAD|';
