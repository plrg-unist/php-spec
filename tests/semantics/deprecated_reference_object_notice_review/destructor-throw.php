<?php
namespace Ns241Throw;
class Base241 {
    #[\Deprecated]
    public const TREE = [1];
    public function __destruct() {
        echo 'D|';
        throw $GLOBALS['exception241'];
    }
}
class Child241 extends Base241 {}
function &selector241() {
    $object241 = new Child241();
    echo 'C|';
    return $object241;
}
function member241() {
    echo 'M|';
    return 'TREE';
}
\set_error_handler(function ($level, $message) {
    echo 'H|';
    return true;
});
$exception241 = new \Exception('selector');
$value241 = 'old';
echo 'B|';
try {
    $value241 = selector241()::{\Ns241Throw\member241()};
} catch (\Exception $seen241) {
    echo $seen241 === $exception241 ? 'E|' : 'BAD|';
}
echo $value241, '|Z|';
\restore_error_handler();
