<?php
namespace {
    #[\Deprecated] const X = [];
    $throwGlobal = true;
    function notice215($level, $message) {
        if ($message === 'Constant X is deprecated') {
            echo 'G|';
            if ($GLOBALS['throwGlobal']) { throw new \Exception('global'); }
        } else { echo 'C|'; }
        return true;
    }
}
namespace Ns215Retry {
    class Base215 { #[\Deprecated] public const C = X; }
    class Child215 extends Base215 {}
    \error_reporting(0);
    \set_error_handler('notice215');
    $value = 'old';
    try { $value = Base215::C; echo 'BAD|'; }
    catch (\Exception $e) { echo 'T|', $value, '|'; }
    $throwGlobal = false;
    $value = Base215::C;
    if ($value === []) { echo 'E|'; } else { echo 'BAD|'; }
    $again = Child215::C;
    if ($again === []) { echo 'E|Z|'; } else { echo 'BAD|'; }
}
