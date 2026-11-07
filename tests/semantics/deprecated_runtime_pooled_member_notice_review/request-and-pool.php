<?php
namespace Ns236Pool;
interface Base236 {
    #[\Deprecated]
    public const TREE = [1];
}
interface Child236 extends Base236 {}
interface Other236 {
    #[\Deprecated]
    public const TREE = 9;
}
function notice236($level, $message) {
    if ($level !== 16384) {
        echo 'BAD|';
        return true;
    }
    if ($message === 'Constant Ns236Pool\\Base236::TREE is deprecated') {
        echo 'H|';
        $inside_prefix236 = $GLOBALS['prefix236'];
        $inside_suffix236 = 'Child236';
        $nested236 = ($inside_prefix236 . $inside_suffix236)::{'TREE'};
        echo 'N|', $nested236[0], '|';
    } elseif ($message === 'Constant Ns236Pool\\Other236::TREE is deprecated') {
        echo 'K|';
    } else {
        echo 'BAD|';
    }
    $GLOBALS['suffix236'] = 'Other236';
    return true;
}
\set_error_handler('Ns236Pool\\notice236');
$prefix236 = '\\nS236pOoL\\';
$suffix236 = 'cHiLd236';
$first236 = ($prefix236 . $suffix236)::{('TR' . 'EE')};
echo 'A|', $first236[0], '|';
$first236[0] = 7;
echo 'MUT|', $first236[0], '|';
$second236 = ($prefix236 . $suffix236)::{'TREE'};
echo 'B|', $second236, '|';
$again236 = Base236::TREE;
echo 'W|', $again236[0], '|Z|';
\restore_error_handler();
