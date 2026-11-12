<?php
namespace Ns239Throw;
class Base239 {
    #[\Deprecated]
    public const TREE = [1];
    public function __destruct() {
        echo 'D|';
        throw $GLOBALS['exception239'];
    }
}
class Child239 extends Base239 {}
function receiver239() {
    echo 'C|';
    return new Child239();
}
function member239() {
    echo 'M|';
    return 'TREE';
}
\set_error_handler(function ($level, $message) {
    echo 'H|';
    return true;
});
$exception239 = new \Exception('selector');
$value239 = 'old';
echo 'B|';
try {
    $value239 = receiver239()::{\Ns239Throw\member239()};
} catch (\Exception $seen239) {
    echo $seen239 === $exception239 ? 'E|' : 'BAD|';
}
echo $value239, '|Z|';
\restore_error_handler();
