<?php
namespace Ns229Method;
class Base229 {
    #[\Deprecated] public const VALUE = 7;
}
class Child229 extends Base229 {}
class Other229 {
    #[\Deprecated] public const VALUE = 9;
}
class Producer229 {
    public function select(): string {
        echo 'M|';
        $GLOBALS['producer229'] = null;
        return $GLOBALS['selected229'];
    }
    public function __destruct() { echo 'D|'; }
}
function notice229($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns229Method\\Base229::VALUE is deprecated' ? 'Hb|' :
        ($level === 16384 && $message === 'Constant Ns229Method\\Other229::VALUE is deprecated' ? 'Ho|' : 'BAD|');
    $GLOBALS['selected229'] = Other229::class;
    return true;
}
$selected229 = Child229::class;
$producer229 = new Producer229();
\set_error_handler('Ns229Method\\notice229');
echo 'B|';
$value229 = ($producer229->select())::VALUE;
echo 'O|', $value229, '|F|';
$producer229 = new Producer229();
$value229 = ($producer229->select())::VALUE;
echo 'O|', $value229, '|Z|';
