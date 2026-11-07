<?php
namespace Ns219Protected;
const DONOR = [1];
class Base219 {
    #[\Deprecated]
    protected const C = \Ns219Protected\DONOR;
    #[\Deprecated]
    public const OPEN = 11;
}
class Child219 extends Base219 {
    public static function get() {
        return parent::C;
    }
}
function notice219($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns219Protected\\Base219::C is deprecated' ? 'H|' : 'BAD|';
    return true;
}
set_error_handler('Ns219Protected\\notice219');
try {
    $discard = Base219::C;
} catch (\Error $error) {
    echo 'C|', $error->getMessage(), '|';
}
$value = Child219::get();
echo $value[0], '|';
$value[0] = 9;
try {
    $discard = Base219::C;
} catch (\Error $error) {
    echo 'W|', $error->getMessage(), '|';
}
$again = Child219::get();
echo $value[0], '|', $again[0], '|Z|';
