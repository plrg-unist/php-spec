<?php
namespace Ns240Ref;
interface I240 {
    #[\Deprecated]
    public const TREE = [1];
}
class Base240 {
    #[\Deprecated]
    public const TREE = [2];
}
function &selector240() {
    global $selector240;
    echo 'C|';
    return $selector240;
}
function notice240($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns240Ref\\I240::TREE is deprecated' || $message === 'Constant Ns240Ref\\Base240::TREE is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['selector240'] = 'Ns240Ref\\Base240';
    unset($GLOBALS['selector240']);
    return true;
}
$selector240 = '\\nS240rEf\\I240';
\set_error_handler('Ns240Ref\\notice240');
echo 'B|';
$first240 = selector240()::TREE;
echo 'R|', $first240[0], '|';
$first240[0] = 7;
echo 'MUT|', $first240[0], '|';
$selector240 = 'Ns240Ref\\Base240';
$again240 = selector240()::TREE;
echo 'W|', $again240[0], '|';
$pool240 = I240::TREE;
echo 'P|', $pool240[0], '|Z|';
\restore_error_handler();
