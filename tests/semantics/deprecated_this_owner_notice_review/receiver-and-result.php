<?php
namespace Ns237Owner;
class Base237 {
    #[\Deprecated]
    public const TREE = [1];
    public function read() {
        return $this::{('TR' . 'EE')};
    }
    public function __destruct() {
        echo 'D|';
    }
}
class Child237 extends Base237 {}
function notice237($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns237Owner\\Base237::TREE is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['receiver237'] = null;
    return true;
}
\set_error_handler('Ns237Owner\\notice237');
$receiver237 = new Child237();
echo 'B|';
$result237 = $receiver237->read();
echo 'O|', $result237[0], '|';
$result237[0] = 7;
echo 'MUT|', $result237[0], '|';
$again237 = Base237::TREE;
echo 'W|', $again237[0], '|Z|';
\restore_error_handler();
