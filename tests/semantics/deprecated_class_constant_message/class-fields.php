<?php
namespace Ns220Class;
use Deprecated as Mark220;
class Base220 {
    #[Mark220(since: '2.0', message: 'Use fresh')]
    public const C = 7;
    #[Mark220('private only', since: null)]
    private const SECRET = 9;
    public static function secret() { return self::SECRET; }
}
class Child220 extends Base220 {}
function notice220($level, $message) {
    echo $message, '|', $level, '|';
    return true;
}
\set_error_handler('Ns220Class\\notice220');
echo Base220::C, '|';
echo Child220::C, '|';
echo \constant('Ns220Class\\Child220::C'), '|';
echo Base220::secret(), '|';
echo 'Z|';
