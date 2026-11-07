<?php
namespace Ns228Value;

interface Base228 {
    #[\Deprecated]
    public const TREE = [1];
    #[\Deprecated]
    public const OTHER = 9;
}
interface Child228 extends Base228 {}
class Implementer228 implements Child228 {}
function take228(): string { echo 'A|'; return $GLOBALS['source228']; }
function other228(): string { echo 'B|'; return 'OTHER'; }
function notice228($level, $message) {
    if ($level === 16384 && $message === 'Constant Ns228Value\\Base228::TREE is deprecated') { echo 'Ht|'; }
    elseif ($level === 16384 && $message === 'Constant Ns228Value\\Base228::OTHER is deprecated') { echo 'Ho|'; }
    else { echo 'BAD|'; }
    $GLOBALS['pick228'] = false;
    $GLOBALS['source228'] = 'OTHER';
    return true;
}

$pick228 = true;
$source228 = 'TREE';
set_error_handler('Ns228Value\\notice228');
$value = Child228::{($pick228 ? \Ns228Value\take228() : \Ns228Value\other228()) . ''};
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'M|', $value[0], '|';
$other = Child228::{($pick228 ? \Ns228Value\take228() : \Ns228Value\other228()) . ''};
echo 'F|', $other, '|';
$again = Implementer228::TREE;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
