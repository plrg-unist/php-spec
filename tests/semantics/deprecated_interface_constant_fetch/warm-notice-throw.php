<?php
namespace {
    $throwNotice = false;
    function notice212($level, $message) {
        echo 'H|';
        if ($GLOBALS['throwNotice']) { throw new \Exception('notice'); }
        return true;
    }
}
namespace Ns212Throw {
    interface Base212 { #[\Deprecated] public const C = 7; }
    interface Child212 extends Base212 {}
    class Impl212 implements Child212 {}
    \set_error_handler('notice212');
    $seed = Base212::C;
    echo 'S|', $seed, '|';
    $throwNotice = true;
    $value = 'old';
    try { $value = Impl212::C; echo 'BAD|'; }
    catch (\Exception $e) { echo 'T|', $value, '|'; }
    $throwNotice = false;
    $again = Child212::C;
    echo 'R|', $again, '|Z|';
}
