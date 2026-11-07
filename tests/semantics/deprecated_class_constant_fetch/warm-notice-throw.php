<?php
namespace {
    $throwNotice = false;
    function notice211($level, $message) {
        echo 'H|';
        if ($GLOBALS['throwNotice']) { throw new \Exception('notice'); }
        return true;
    }
}
namespace Ns211Throw {
    class Base211 { #[\Deprecated] public const C = 7; }
    class Child211 extends Base211 {}
    \set_error_handler('notice211');
    $seed = Base211::C;
    echo 'S|', $seed, '|';
    $throwNotice = true;
    $value = 'old';
    try { $value = Child211::C; echo 'BAD|'; }
    catch (\Exception $e) { echo 'T|', $value, '|'; }
    $throwNotice = false;
    $again = Child211::C;
    echo 'R|', $again, '|Z|';
}
