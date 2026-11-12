<?php
namespace Ns246Float;
class Base246 {
    public $tag;
    public function __destruct() {
        echo 'D|', $this->tag === 1.5 ? 'F|' : 'BAD|';
        $GLOBALS['member246'] = 'B';
    }
}
class Single246 extends Base246 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
class Wide246 extends Base246 {
    public $pad;
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &single246() {
    $receiver246 = new Single246();
    $receiver246->tag = 1.5;
    echo 'S|';
    return $receiver246;
}
function &wide246() {
    $receiver246 = new Wide246();
    $receiver246->pad = false;
    $receiver246->tag = 1.5;
    echo 'W|';
    return $receiver246;
}
function member246() {
    echo 'M|';
    return $GLOBALS['member246'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns246Float\\Single246::B is deprecated' || $message === 'Constant Ns246Float\\Wide246::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member246'] = 'A';
    return true;
});
$member246 = 'A';
echo 'B|', single246()::{member246()}, '|Z|';
echo 'B|', wide246()::{member246()}, '|Z|';
\restore_error_handler();
