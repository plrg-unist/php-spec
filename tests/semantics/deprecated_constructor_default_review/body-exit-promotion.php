<?php
#[Deprecated] const X = [];
function notice198() { echo 'H|'; return true; }
class Box198 {
    function __construct(public array $value = X) {
        echo 'C|';
        echo $this->value === [] ? 'E|' : 'BAD|';
        $GLOBALS['held'] = $this;
        exit(7);
    }
    function __destruct() { echo 'R|'; }
}
function finish198() {
    echo 'S|';
    $object = $GLOBALS['held'];
    echo $object->value === [] ? 'E|' : 'BAD|';
    $GLOBALS['held'] = null;
    $object = null;
    echo 'Z|';
}
$held = null;
set_error_handler('notice198');
register_shutdown_function('finish198');
new Box198;
echo 'BAD|';
