<?php
namespace Ns242RetainedChild;
class Payload242 {
    public function __destruct() {
        echo 'P|';
    }
}
class Base242 {
    public $payload;
    #[\Deprecated]
    public const TREE = [1], OTHER = [4];
    public function __destruct() {
        echo 'D|', Child242::TREE[0], '|';
        $GLOBALS['member242'] = 'TREE';
    }
}
class Child242 extends Base242 {
    #[\Deprecated]
    public const TREE = [2], OTHER = [3];
}
function &selector242() {
    $receiver242 = new Child242();
    $receiver242->payload = $GLOBALS['payload242'];
    echo 'C|';
    return $receiver242;
}
function member242() {
    echo 'M|';
    return $GLOBALS['member242'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns242RetainedChild\\Child242::TREE is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member242'] = 'OTHER';
    return true;
});
$payload242 = new Payload242();
$member242 = 'OTHER';
echo 'B|';
$value242 = selector242()::{member242()};
echo 'R|', $value242[0], '|';
$value242[0] = 7;
echo 'MUT|', $value242[0], '|';
unset($payload242);
echo 'W|', Child242::TREE[0], '|Z|';
\restore_error_handler();
