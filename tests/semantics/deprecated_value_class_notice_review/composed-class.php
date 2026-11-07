<?php
namespace Ns229Value;

interface Base229 {
    #[\Deprecated]
    public const TREE = [1];
}
interface Child229 extends Base229 {}
class Implementer229 implements Child229 {}
interface Other229 {
    #[\Deprecated]
    public const TREE = 9;
}
function fail229(): string { echo 'T|'; throw new \Exception('stop'); }
function take229(): string { echo 'A|'; return $GLOBALS['class229']; }
function other229(): string { echo 'B|'; return 'Ns229Value\\Other229'; }
function notice229($level, $message) {
    if ($level === 16384 && $message === 'Constant Ns229Value\\Base229::TREE is deprecated') { echo 'Ht|'; }
    elseif ($level === 16384 && $message === 'Constant Ns229Value\\Other229::TREE is deprecated') { echo 'Ho|'; }
    else { echo 'BAD|'; }
    $GLOBALS['pick229'] = false;
    $GLOBALS['class229'] = 'Ns229Value\\Other229';
    return true;
}

$pick229 = true;
$class229 = '\\nS229vAlUe\\cHiLd229';
set_error_handler('Ns229Value\\notice229');
$failed = 'old';
try { $failed = (\Ns229Value\fail229())::MISSING; }
catch (\Exception $e) { echo 'C|', $failed, '|'; }
$value = (($pick229 ? \Ns229Value\take229() : \Ns229Value\other229()) . '')::TREE;
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'M|', $value[0], '|';
$other = (($pick229 ? \Ns229Value\take229() : \Ns229Value\other229()) . '')::TREE;
echo 'F|', $other, '|';
$again = Implementer229::TREE;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
