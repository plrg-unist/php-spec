<?php
#[Deprecated] const X = [];
class Local198 {
    function __destruct() { echo 'L|'; $GLOBALS['seen'] = 7; }
}
function notice198() {
    echo 'H|';
    $local = new Local198;
    return true;
}
class Box198 {
    function __construct(public array $value = X) { echo 'C|'; }
    function __destruct() { echo 'R|'; }
}
$seen = 0;
set_error_handler('notice198');
$first = new Box198;
echo $seen, '|';
echo $first->value === [] ? 'E|' : 'BAD|';
$first->value[] = 8;
$second = new Box198;
echo $second->value === [] ? 'E|' : 'BAD|';
echo $first->value[0], '|';
$first = null;
$second = null;
