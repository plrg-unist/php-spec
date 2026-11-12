<?php
namespace Ns256UnionValues;
class Base256 {
    public int|float $integer;
    public float|int $floating;
    public string|int $text;
    public false|string $onlyFalse;
    public int|true $onlyTrue;
    public null|bool|int $nothing;
    public float|string|bool $boolean;
    public null|string|int|bool|float $request;
    public function __destruct() {
        echo 'D|';
        echo $this->integer === 17 ? 'I|' : 'BAD|';
        echo $this->floating === 1.5 ? 'F|' : 'BAD|';
        echo $this->text === 'wire256' ? 'S|' : 'BAD|';
        echo $this->onlyFalse === false ? 'F|' : 'BAD|';
        echo $this->onlyTrue === true ? 'T|' : 'BAD|';
        echo $this->nothing === null ? 'N|' : 'BAD|';
        echo $this->boolean === false ? 'B|' : 'BAD|';
        echo $this->request === 'req256' ? 'R|' : 'BAD|';
        $GLOBALS['member256values'] = 'B';
    }
}
class Wide256 extends Base256 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &selector256() {
    $receiver256 = new Wide256();
    $receiver256->integer = 17;
    $receiver256->floating = 1.5;
    $receiver256->text = 'wire256';
    $receiver256->onlyFalse = false;
    $receiver256->onlyTrue = true;
    $receiver256->nothing = null;
    $receiver256->boolean = false;
    $suffix256 = '256';
    $receiver256->request = 'req' . $suffix256;
    echo 'W|';
    return $receiver256;
}
function member256() {
    echo 'M|';
    return $GLOBALS['member256values'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns256UnionValues\\Wide256::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member256values'] = 'A';
    return true;
});
$member256values = 'A';
echo 'B|', selector256()::{member256()}, '|Z|';
\restore_error_handler();
