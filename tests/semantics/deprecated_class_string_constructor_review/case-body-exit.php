<?php
#[Deprecated] const X = [];
class Other199 {}
function notice199() {
    echo 'H|';
    $GLOBALS['selector'] = 'Other199';
    return true;
}
class CaseExit199 {
    function __construct(public array $value = X) {
        echo 'C|';
        echo $this->value === [] ? 'E|' : 'BAD|';
        $GLOBALS['held'] = $this;
        exit(7);
    }
    function __destruct() { echo 'BAD-R|'; }
}
function finish199() {
    echo 'S|';
    $object = $GLOBALS['held'];
    echo $object->value === [] ? 'E|' : 'BAD|';
    $GLOBALS['held'] = null;
    $object = null;
    echo 'Z|';
}
$held = null;
$selector = '\\cAsEeXiT199';
set_error_handler('notice199');
register_shutdown_function('finish199');
new $selector;
echo 'BAD|';
