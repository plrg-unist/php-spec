<?php
#[Deprecated] const X = [1];
class Base187 {
    public function take($value = X) {
        echo self::class, '/', static::class, ':', $value[0], '|';
        return 7;
    }
    public function __destruct() { echo 'D|'; }
}
class Child187 extends Base187 {}
$receiver = new Child187();
set_error_handler(function() {
    global $receiver;
    echo 'H|';
    $receiver = null;
    return true;
});
$result = $receiver->take();
echo $result, '|';
