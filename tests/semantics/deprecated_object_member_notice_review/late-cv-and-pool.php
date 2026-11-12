<?php
namespace Ns239Pool;
class Base239 {
    #[\Deprecated]
    public const TREE = [1];
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member239'] = 'TREE';
    }
}
class Child239 extends Base239 {
    #[\Deprecated]
    public const TREE = [2];
    public const A = 99;
}
function receiver239() {
    echo 'C|';
    return new Child239();
}
function notice239($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns239Pool\\Child239::TREE is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member239'] = 'A';
    return true;
}
$member239 = 'A';
\set_error_handler('Ns239Pool\\notice239');
echo 'B|';
$first239 = receiver239()::{$member239};
echo 'R|', $first239[0], '|';
$first239[0] = 7;
echo 'MUT|', $first239[0], '|';
$again239 = receiver239()::{('TR' . 'EE')};
echo 'W|', $again239[0], '|Z|';
\restore_error_handler();
