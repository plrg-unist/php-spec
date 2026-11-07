<?php
namespace Ns227Member;

interface Base227 {
    #[\Deprecated]
    public const TREE = [1];
    #[\Deprecated]
    public const OTHER = 9;
}
interface Child227 extends Base227 {}
class Implementer227 implements Child227 {}
function member227(): string {
    echo 'M|';
    if ($GLOBALS['throw227']) { throw new \Exception('member227'); }
    return $GLOBALS['member227'];
}
function notice227($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns227Member\\Base227::TREE is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member227'] = null;
    return true;
}

$throw227 = true;
$member227 = 'TREE';
$value = 'old';
set_error_handler('Ns227Member\\notice227');
try { $value = Absent227::{\Ns227Member\member227()}; }
catch (\Exception $exception) { echo 'T|', $value, '|'; }
$throw227 = false;
$value = Child227::{\Ns227Member\member227()};
echo 'O|', $value[0], '|';
$value[0] = 7;
echo 'MUT|', $value[0], '|';
$again = Implementer227::TREE;
echo 'W|', $again[0], '|Z|';
restore_error_handler();
