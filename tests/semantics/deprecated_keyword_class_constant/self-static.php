<?php
namespace Ns218Scope;
\define('SCALAR218', 7);
class Base218 {
    #[\Deprecated] public const C = \SCALAR218;
    public static function read() {
        echo 'S|', self::C, '|L|', static::C, '|';
    }
}
class Child218 extends Base218 {
    #[\Deprecated] public const C = 9;
}
function notice218($level, $message) {
    echo $message === 'Constant Ns218Scope\\Base218::C is deprecated' ? 'B|' : 'C|';
    return true;
}
\set_error_handler('Ns218Scope\\notice218');
Base218::read();
Child218::read();
echo 'Z|';
