<?php
namespace Ns228Method;
class Target228 {
    #[\Deprecated] public const VALUE = 7;
}
class Producer228 {
    public function member(): string {
        echo 'M|';
        $GLOBALS['producer228'] = null;
        return 'VALUE';
    }
    public function __destruct() { echo 'D|'; }
}
function notice228($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns228Method\\Target228::VALUE is deprecated' ? 'H|' : 'BAD|';
    return true;
}
$producer228 = new Producer228();
\set_error_handler('Ns228Method\\notice228');
echo 'B|';
$value228 = Target228::{$producer228->member()};
echo 'O|', $value228, '|Z|';
