<?php
#[Deprecated] const X = [];
function notice200() { echo 'H|'; return true; }
class Root200 {
    function __construct(public array $value = X) {
        echo 'C|', static::class, '|';
        echo $this->value === [] ? 'E|' : 'BAD|';
        $GLOBALS['held'] = $this;
        exit(7);
    }
    function __destruct() { echo 'BAD-D|'; }
}
class Base200 extends Root200 {
    static function makeSelf() { return new self; }
}
class Leaf200 extends Base200 {}
function finish200() {
    echo 'S|';
    $object = $GLOBALS['held'];
    echo $object->value === [] ? 'E|' : 'BAD|';
    $GLOBALS['held'] = null;
    $object = null;
    echo 'Z|';
}
$held = null;
set_error_handler('notice200');
register_shutdown_function('finish200');
Leaf200::makeSelf();
echo 'BAD|';
