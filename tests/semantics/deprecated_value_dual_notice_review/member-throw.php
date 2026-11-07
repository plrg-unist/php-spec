<?php
namespace Ns230Value;

interface Base230 {
    #[\Deprecated]
    public const TREE = [1];
}
interface Child230 extends Base230 {}
class Implementer230 implements Child230 {}
interface Other230 {
    #[\Deprecated]
    public const TREE = 9;
}
function class230(): string { echo 'C|'; return $GLOBALS['class230']; }
function member230(): string {
    echo 'M|';
    $GLOBALS['class230'] = 'Ns230Value\\Other230';
    if ($GLOBALS['throw230']) {
        $GLOBALS['throw230'] = false;
        throw new \Exception('stop');
    }
    return 'TREE';
}
function notice230($level, $message) {
    if ($level === 16384 && $message === 'Constant Ns230Value\\Base230::TREE is deprecated') { echo 'Ht|'; }
    elseif ($level === 16384 && $message === 'Constant Ns230Value\\Other230::TREE is deprecated') { echo 'Ho|'; }
    else { echo 'BAD|'; }
    return true;
}

$class230 = 'Ns230Value\\Child230';
$throw230 = true;
set_error_handler('Ns230Value\\notice230');
$value = 'old';
try { $value = (\Ns230Value\class230())::{\Ns230Value\member230()}; }
catch (\Exception $e) { echo 'T|', $value, '|'; }
$class230 = 'Ns230Value\\Child230';
$value = (\Ns230Value\class230())::{\Ns230Value\member230()};
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'MUT|', $value[0], '|';
$other = (\Ns230Value\class230())::{\Ns230Value\member230()};
echo 'F|', $other, '|';
$again = Implementer230::TREE;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
