<?php
namespace Ns216Closure;
const BASE = static function () {
    echo __CLASS__ === '' ? 'L|' : 'BAD|';
};
#[\Deprecated]
const OWNED = BASE;
interface Base216 {
    #[\Deprecated]
    public const VALUE = \Ns216Closure\OWNED;
}
interface Child216 extends Base216 {}
class Implementer216 implements Child216 {}
function notice216($level, $message, $file, $line) {
    echo $message === 'Constant Ns216Closure\\OWNED is deprecated' ? 'G|' : 'C|';
    return true;
}
set_error_handler('Ns216Closure\\notice216');
$first = \constant('Ns216Closure\\Base216::VALUE');
$second = \constant('Ns216Closure\\Child216::VALUE');
$third = \constant('Ns216Closure\\Implementer216::VALUE');
echo $first === BASE && $second === BASE && $third === BASE ? 'same|' : 'BAD|';
$first();
restore_error_handler();
echo 'Z|';
