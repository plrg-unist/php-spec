<?php
namespace Ns241Retarget;
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
class Other241 {
    public const TREE = [3];
}
function &selector241() {
    global $selector241;
    echo 'C|';
    return $selector241;
}
function member241() {
    echo 'M|';
    return 'TREE';
}
function notice241($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns241Retarget\\Child241::TREE is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['selector241'] = new Other241();
    return true;
}
$selector241 = new Child241();
\set_error_handler('Ns241Retarget\\notice241');
echo 'B|';
$first241 = selector241()::{\Ns241Retarget\member241()};
echo 'R|', $first241[0], '|';
$later241 = $selector241::TREE;
echo 'W|', $later241[0], '|Z|';
\restore_error_handler();
