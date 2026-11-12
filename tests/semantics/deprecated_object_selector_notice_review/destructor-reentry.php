<?php
namespace Ns238Reentry;
class Base238 {
    #[\Deprecated]
    public const A = 7;
    public function __destruct() {
        echo 'D|', Child238::A, '|';
    }
}
class Child238 extends Base238 {
    #[\Deprecated]
    public const A = 9;
}
function receiver238() {
    echo 'C|';
    return new Child238();
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns238Reentry\\Child238::A is deprecated' ? 'H|' : 'BAD|';
    return true;
});
echo 'B|', receiver238()::A, '|Z|';
\restore_error_handler();
