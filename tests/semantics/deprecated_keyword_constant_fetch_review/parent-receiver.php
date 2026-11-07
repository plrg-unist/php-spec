<?php
namespace Ns218Parent;
const DONOR = [1];
class Base218 {
    #[\Deprecated]
    public const C = \Ns218Parent\DONOR;
}
class Child218 extends Base218 {
    public function get() {
        return parent::C;
    }
    public function __destruct() {
        echo 'D|';
    }
}
function notice218($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns218Parent\\Base218::C is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['receiver'] = null;
    return true;
}
set_error_handler('Ns218Parent\\notice218');
$GLOBALS['receiver'] = new Child218();
$value = $GLOBALS['receiver']->get();
echo 'R|', $value[0], '|';
$again = Base218::C;
echo 'W|', $again[0], '|Z|';
