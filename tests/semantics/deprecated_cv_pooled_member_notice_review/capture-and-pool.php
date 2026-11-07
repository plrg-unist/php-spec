<?php
namespace Ns235Pool;
interface Base235 {
    #[\Deprecated]
    public const TREE = [1];
}
interface Child235 extends Base235 {}
interface Other235 {
    #[\Deprecated]
    public const TREE = 9;
}
function notice235($level, $message) {
    if ($level !== 16384) {
        echo 'BAD|';
        return true;
    }
    if ($message === 'Constant Ns235Pool\\Base235::TREE is deprecated') {
        echo 'H|';
        $inside235 = 'Ns235Pool\\Child235';
        $nested235 = $inside235::{'TREE'};
        echo 'N|', $nested235[0], '|';
    } elseif ($message === 'Constant Ns235Pool\\Other235::TREE is deprecated') {
        echo 'K|';
    } else {
        echo 'BAD|';
    }
    $GLOBALS['class235'] = 'Ns235Pool\\Other235';
    return true;
}
\set_error_handler('Ns235Pool\\notice235');
$class235 = '\\nS235pOoL\\cHiLd235';
$first235 = $class235::{('TR' . 'EE')};
echo 'A|', $first235[0], '|';
$first235[0] = 7;
echo 'MUT|', $first235[0], '|';
$second235 = $class235::{'TREE'};
echo 'B|', $second235, '|';
$again235 = Base235::TREE;
echo 'W|', $again235[0], '|Z|';
\restore_error_handler();
