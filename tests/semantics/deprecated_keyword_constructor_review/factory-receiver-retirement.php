<?php
#[Deprecated] const X = [];
function notice200() {
    echo 'H|';
    $GLOBALS['factory'] = null;
    return true;
}
class Root200 {
    public $value;
    function __construct($value = X) {
        $this->value = $value;
        echo 'C|', static::class, '|', ($value === [] ? 'E|' : 'N|');
    }
    function __destruct() { echo 'D|', static::class, '|'; }
}
class Base200 extends Root200 {
    function makeParent() {
        echo 'F|';
        return new parent;
    }
}
class Leaf200 extends Base200 {}
$factory = new Leaf200(9);
set_error_handler('notice200');
$answer = $factory->makeParent();
echo 'R|';
echo $factory === null ? 'G|' : 'BAD|';
echo $answer->value === [] ? 'E|' : 'BAD|';
$answer = null;
echo 'Z|';
