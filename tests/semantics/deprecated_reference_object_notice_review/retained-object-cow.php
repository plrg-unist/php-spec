<?php
namespace Ns241Retained;
class Base241 {
    #[\Deprecated]
    public const TREE = [1];
    public function __destruct() {
        echo 'D|';
        $inner241 = Child241::TREE;
        echo 'V|', $inner241[0], '|';
    }
}
class Child241 extends Base241 {
    #[\Deprecated]
    public const TREE = [2];
}
function &selector241() {
    global $selector241;
    echo 'C|';
    return $selector241;
}
function notice241($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns241Retained\\Child241::TREE is deprecated' ? 'H|' : 'BAD|';
    unset($GLOBALS['selector241']);
    return true;
}
$selector241 = new Child241();
\set_error_handler('Ns241Retained\\notice241');
echo 'B|';
$first241 = selector241()::TREE;
echo 'R|', $first241[0], '|';
$first241[0] = 7;
echo 'MUT|', $first241[0], '|';
$again241 = Child241::TREE;
echo 'W|', $again241[0], '|Z|';
\restore_error_handler();
