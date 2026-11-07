<?php
namespace Ns215Closure;
const BASE = static function () {
    echo __CLASS__ === '' ? 'L|' : 'BAD|';
};
#[\Deprecated]
const OWNED = BASE;
interface Base215 {
    #[\Deprecated]
    public const VALUE = \Ns215Closure\OWNED;
}
interface Child215 extends Base215 {}
class Implementer215 implements Child215 {}
function notice215($level, $message, $file, $line) {
    echo $message === 'Constant Ns215Closure\\OWNED is deprecated' ? 'G|' : 'C|';
    return true;
}
set_error_handler('Ns215Closure\\notice215');
$first = Base215::VALUE;
$second = Child215::VALUE;
$third = Implementer215::VALUE;
echo $first === BASE && $second === BASE && $third === BASE ? 'same|' : 'BAD|';
$first();
restore_error_handler();
echo 'Z|';
