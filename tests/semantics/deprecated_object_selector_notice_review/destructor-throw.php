<?php
namespace Ns238Throw;
class Base238 {
    #[\Deprecated]
    public const TREE = [1];
    public function __destruct() {
        echo 'D|';
        throw $GLOBALS['exception238'];
    }
}
class Child238 extends Base238 {}
function receiver238() {
    echo 'C|';
    return new Child238();
}
\set_error_handler(function ($level, $message) {
    echo 'H|';
    return true;
});
$exception238 = new \Exception('selector');
$value238 = 'old';
echo 'B|';
try {
    $value238 = receiver238()::TREE;
} catch (\Exception $seen238) {
    echo $seen238 === $exception238 ? 'E|' : 'BAD|';
}
echo $value238, '|Z|';
\restore_error_handler();
