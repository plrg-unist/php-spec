<?php
namespace Ns244Nested;
class Shared244 {
    public function __destruct() {
        echo 'G|';
        $GLOBALS['member244'] = 'B';
    }
}
class Retained244 {
    public function __destruct() {
        echo 'E|';
    }
}
class Middle244 {
    public $deep, $tag, $retained;
    public function __destruct() {
        echo 'I|', Child244::A, '|';
    }
}
class Base244 {
    public $head, $flag, $empty;
    #[\Deprecated]
    public const A = 7, B = 8;
    public function __destruct() {
        echo 'D|', Child244::A, '|';
    }
}
class Child244 extends Base244 {
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &selector244() {
    $shared244 = new Shared244();
    $GLOBALS['retained244'] = new Retained244();
    $middle244 = new Middle244();
    $middle244->deep = $shared244;
    $middle244->tag = 0;
    $middle244->retained = $GLOBALS['retained244'];
    $receiver244 = new Child244();
    $receiver244->tail = $shared244;
    $receiver244->flag = false;
    $receiver244->head = $middle244;
    unset($middle244, $shared244);
    echo 'C|';
    return $receiver244;
}
function member244() {
    echo 'M|';
    return $GLOBALS['member244'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns244Nested\\Child244::A is deprecated' || $message === 'Constant Ns244Nested\\Child244::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member244'] = 'A';
    return true;
});
$member244 = 'A';
echo 'B|', selector244()::{member244()}, '|Z|';
unset($retained244);
\restore_error_handler();
