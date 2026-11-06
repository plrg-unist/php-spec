<?php
#[Deprecated] const X = [];
class Other199 {}
class Local199 {
    function __destruct() {
        echo 'L|';
        $GLOBALS['selector'] = 'Other199';
    }
}
function notice199() {
    echo 'H|';
    $local = new Local199;
    return true;
}
class Box199 {
    function __construct(public array $value = X) { echo 'C|'; }
    function __destruct() { echo 'R|'; }
}
$selector = 'Box199';
set_error_handler('notice199');
$first = new $selector;
echo $selector === 'Other199' ? 'B|' : 'BAD|';
echo $first->value === [] ? 'E|' : 'BAD|';
$first = null;
$next = 'Box199';
$again = new $next;
echo $again->value === [] ? 'E|' : 'BAD|';
$again = null;
