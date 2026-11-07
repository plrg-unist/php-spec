<?php
namespace Ns220Interface {
    use Deprecated as Mark;
    interface Base220 {
        #[Mark(message: null, since: '8.5')]
        public const SINCE_ONLY = 7;
        #[Mark(since: null, message: '')]
        public const QUIET = 8, OTHER = 9;
    }
    interface Child220 extends Base220 {}
    class Implementer220 implements Child220 {}
}
namespace Ns220Reader {
    function notice220($level, $message) {
        echo $level === 16384 ? $message : 'BAD';
        echo '|';
        return true;
    }
    set_error_handler('Ns220Reader\\notice220');
    echo \Ns220Interface\Base220::SINCE_ONLY, '|';
    echo \constant('Ns220Interface\\Child220::SINCE_ONLY'), '|';
    echo \Ns220Interface\Implementer220::QUIET, '|';
    echo \constant('Ns220Interface\\Base220::QUIET'), '|';
    echo \Ns220Interface\Child220::OTHER, '|';
    echo \constant('Ns220Interface\\Implementer220::OTHER'), '|';
    restore_error_handler();
    echo 'Z|';
}
