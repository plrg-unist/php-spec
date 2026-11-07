<?php
namespace Ns231Object;

interface Base231 {
    #[\Deprecated]
    public const TREE = [1];
}
interface Child231 extends Base231 {}
class Impl231 implements Child231 {
    public function __destruct() { echo 'D|'; }
}
function member231(): string {
    echo 'M|';
    $GLOBALS['class231'] = null;
    echo 'R|';
    return 'TREE';
}
function notice231($level, $message) {
    if ($level === 16384 && $message === 'Constant Ns231Object\\Base231::TREE is deprecated') { echo 'H|'; }
    else { echo 'BAD|'; }
    return true;
}

$class231 = new Impl231;
set_error_handler('Ns231Object\\notice231');
$value = $class231::{\Ns231Object\member231()};
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'MUT|', $value[0], '|';
$again = Impl231::TREE;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
