<?php
namespace Ns234Protected;
class Base234 {
    #[\Deprecated]
    protected const TREE = [1];
}
class Child234 extends Base234 {
    public static function read() {
        $class234 = 'Ns234Protected\\Child234';
        $member234 = 'TREE';
        $first234 = $class234::{$member234};
        echo 'A|', $first234[0], '|';
        $first234[0] = 7;
        echo 'MUT|', $first234[0], '|';
        $second234 = ('\\nS234pRoTeCtEd\\cHiLd234')::{('TR' . 'EE')};
        echo 'B|', $second234[0], '|';
        return $second234;
    }
    public static function plain() {
        return parent::TREE;
    }
}
function notice234($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns234Protected\\Base234::TREE is deprecated' ? 'H|' : 'BAD|';
    return true;
}
\set_error_handler('Ns234Protected\\notice234');
$class234 = 'Ns234Protected\\Child234';
$member234 = 'TREE';
echo 'C|';
try {
    $denied234 = $class234::{$member234};
} catch (\Error $error234) {
    echo $error234->getMessage(), '|';
}
echo 'S|';
$result234 = Child234::read();
echo 'R|', $result234[0], '|';
$plain234 = Child234::plain();
echo 'L|', $plain234[0], '|';
echo 'W|';
try {
    $denied234 = ('\\nS234pRoTeCtEd\\cHiLd234')::{('TR' . 'EE')};
} catch (\Error $error234) {
    echo $error234->getMessage(), '|';
}
echo 'Z|';
\restore_error_handler();
