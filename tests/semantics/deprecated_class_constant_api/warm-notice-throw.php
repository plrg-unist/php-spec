<?php
\define('CACHESEED213', 7);
$throwNotice = false;
function notice213($level, $message) {
    echo 'H|';
    if ($GLOBALS['throwNotice']) { throw new \Exception('notice'); }
    return true;
}
class Base213 { #[\Deprecated] public const C = \CACHESEED213; }
class Child213 extends Base213 {}
\set_error_handler('notice213');
$seed = Base213::C;
echo 'S|', $seed, '|';
$throwNotice = true;
$value = 'old';
try { $value = \constant('Child213::C'); echo 'BAD|'; }
catch (\Exception $e) { echo 'T|', $value, '|'; }
$throwNotice = false;
$again = \constant('Base213::C');
echo 'R|', $again, '|Z|';
