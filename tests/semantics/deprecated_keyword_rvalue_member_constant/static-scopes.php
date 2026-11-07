<?php
namespace Ns232Static;
class Base232 {
    #[\Deprecated] public const A = 7;
    #[\Deprecated] public const B = 8;
    public static function run() {
        echo 'S|';
        echo self::{\Ns232Static\member232()}, '|';
        echo 'T|';
        echo static::{\Ns232Static\member232()}, '|';
    }
}
class Child232 extends Base232 {
    #[\Deprecated] public const B = 9;
}
function member232(): string {
    echo 'M|';
    return $GLOBALS['member232'];
}
function notice232($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns232Static\\Base232::A is deprecated' ? 'Ha|' :
        ($level === 16384 && $message === 'Constant Ns232Static\\Base232::B is deprecated' ? 'Hb|' :
        ($level === 16384 && $message === 'Constant Ns232Static\\Child232::B is deprecated' ? 'Hc|' : 'BAD|'));
    $GLOBALS['member232'] = 'B';
    return true;
}
\set_error_handler('Ns232Static\\notice232');
$member232 = 'A';
Base232::run();
$member232 = 'A';
Child232::run();
echo 'Z|';
