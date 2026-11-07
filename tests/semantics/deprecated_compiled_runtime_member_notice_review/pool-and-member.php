<?php
namespace Ns233Pool;

interface Base233 {
    #[\Deprecated]
    public const TREE = [1];
}
interface Child233 extends Base233 {}
class Impl233 implements Child233 {}
interface Other233 {
    #[\Deprecated]
    public const TREE = 9;
}
function member233(): string { echo 'M|'; return $GLOBALS['member233']; }
function notice233($level, $message) {
    if ($level === 16384 && $message === 'Constant Ns233Pool\\Base233::TREE is deprecated') { echo 'H|'; }
    else { echo 'BAD|'; }
    $GLOBALS['member233'] = null;
    return true;
}

$member233 = 'TREE';
set_error_handler('Ns233Pool\\notice233');
$value = ('\\nS233pOoL\\cHiLd233')::{\Ns233Pool\member233()};
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'MUT|', $value[0], '|';
$member233 = 'TREE';
$second = ('Ns233Pool\\Impl' . '233')::{\Ns233Pool\member233()};
echo 'B|', $second[0], '|';
$again = Base233::TREE;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
