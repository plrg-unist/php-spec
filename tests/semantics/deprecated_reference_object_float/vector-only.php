<?php
namespace Ns246Vector;
class Base246 {
    public $tag;
    public function __destruct() {
        echo 'D|', $this->tag === 1.5 ? 'F|' : 'BAD|';
        $GLOBALS['member246vector'] = 'B';
    }
}
class Wide246 extends Base246 {
    public $pad;
    #[\Deprecated]
    public const A = 9, B = 10;
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
    return $GLOBALS['member246vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns246Vector\\Wide246::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member246vector'] = 'A';
    return true;
});
$member246vector = 'A';
echo 'B|', wide246()::{member246()}, '|Z|';
\restore_error_handler();
