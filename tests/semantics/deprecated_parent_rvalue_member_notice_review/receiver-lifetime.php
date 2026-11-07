<?php
namespace Ns232Parent;

class Base232 {
    #[\Deprecated]
    public const TREE = [1];
}
class Child232 extends Base232 {
    public function read() { return parent::{\Ns232Parent\member232()}; }
    public function __destruct() { echo 'D|'; }
}
function member232(): string {
    echo 'M|';
    $GLOBALS['receiver232'] = null;
    echo 'R|';
    return 'TREE';
}
function notice232($level, $message) {
    if ($level === 16384 && $message === 'Constant Ns232Parent\\Base232::TREE is deprecated') { echo 'H|'; }
    else { echo 'BAD|'; }
    return true;
}

$receiver232 = new Child232;
set_error_handler('Ns232Parent\\notice232');
$value = $receiver232->read();
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'MUT|', $value[0], '|';
$again = Base232::TREE;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
