<?php
#[Deprecated] const X = [];
class Base187 {
    public static function shared($value = X) {
        echo self::class, '/', static::class, ':', isset($value[0]) ? 'N|' : 'E|';
    }
    public function own($value = X) {
        echo self::class, '/', static::class, ':', isset($value[0]) ? 'N|' : 'E|';
    }
}
class Child187 extends Base187 {}
set_error_handler(function() { echo 'H|'; return true; });
Base187::shared(); Child187::shared(); Base187::shared();
$receiver = new Child187();
$receiver->own(); $receiver->own();
