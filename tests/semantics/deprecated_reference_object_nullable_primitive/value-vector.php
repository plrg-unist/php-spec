<?php
namespace Ns255NullableValues;
class Base255 {
    public int|null $i;
    public float|null $f;
    public string|null $s;
    public bool|null $b;
    public false|null $onlyFalse;
    public true|null $onlyTrue;
    public function __destruct() {
        echo 'D|';
        echo $this->i === 17 ? 'I|' : 'BAD|';
        echo $this->f === 1.5 ? 'F|' : 'BAD|';
        echo $this->s === 'wire255' ? 'S|' : 'BAD|';
        echo $this->b === false ? 'B|' : 'BAD|';
        echo $this->onlyFalse === false ? 'F|' : 'BAD|';
        echo $this->onlyTrue === true ? 'T|' : 'BAD|';
        $GLOBALS['member255values'] = 'B';
    }
}
class Wide255 extends Base255 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &selector255() {
    $receiver255 = new Wide255();
    $receiver255->i = 17;
    $receiver255->f = 1.5;
    $receiver255->s = 'wire255';
    $receiver255->b = false;
    $receiver255->onlyFalse = false;
    $receiver255->onlyTrue = true;
    echo 'W|';
    return $receiver255;
}
function member255() {
    echo 'M|';
    return $GLOBALS['member255values'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns255NullableValues\\Wide255::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member255values'] = 'A';
    return true;
});
$member255values = 'A';
echo 'B|', selector255()::{member255()}, '|Z|';
\restore_error_handler();
