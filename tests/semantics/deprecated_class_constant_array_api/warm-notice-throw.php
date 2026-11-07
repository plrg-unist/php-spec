<?php
$throwNotice = false;
function notice214($level, $message) {
    echo 'H|';
    if ($GLOBALS['throwNotice']) { throw new \Exception('notice'); }
    return true;
}
class Base214 { #[\Deprecated] public const C = [7]; }
class Child214 extends Base214 {}
\set_error_handler('notice214');
$seed = \constant('Base214::C');
echo 'S|', $seed[0], '|';
$throwNotice = true;
$value = 'old';
try { $value = \constant('Child214::C'); echo 'BAD|'; }
catch (\Exception $e) { echo 'T|', $value, '|'; }
$throwNotice = false;
$again = \constant('Base214::C');
echo 'R|', $again[0], '|Z|';
