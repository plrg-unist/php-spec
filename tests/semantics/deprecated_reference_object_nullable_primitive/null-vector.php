<?php
namespace Ns255NullableNulls;
class Base255 {
    public ?int $i;
    public ?float $f;
    public ?string $s;
    public ?bool $b;
    public ?false $onlyFalse;
    public ?true $onlyTrue;
    public function __destruct() {
        echo 'D|';
        echo $this->i === null ? 'N|' : 'BAD|';
        echo $this->f === null ? 'N|' : 'BAD|';
        echo $this->s === null ? 'N|' : 'BAD|';
        echo $this->b === null ? 'N|' : 'BAD|';
        echo $this->onlyFalse === null ? 'N|' : 'BAD|';
        echo $this->onlyTrue === null ? 'N|' : 'BAD|';
        $GLOBALS['member255nulls'] = 'B';
    }
}
class Wide255 extends Base255 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &selector255() {
    $receiver255 = new Wide255();
    $receiver255->i = null;
    $receiver255->f = null;
    $receiver255->s = null;
    $receiver255->b = null;
    $receiver255->onlyFalse = null;
    $receiver255->onlyTrue = null;
    echo 'W|';
    return $receiver255;
}
function member255() {
    echo 'M|';
    return $GLOBALS['member255nulls'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns255NullableNulls\\Wide255::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member255nulls'] = 'A';
    return true;
});
$member255nulls = 'A';
echo 'B|', selector255()::{member255()}, '|Z|';
\restore_error_handler();
