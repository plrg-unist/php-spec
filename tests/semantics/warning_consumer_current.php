<?php
class Prior213 {
    public static int $value = 7;
    public static function &get() { return self::$value; }
}
class HandlerCache213 {
    const Closure H = static function($level, $message, $file, $line) {
        Prior213::$value = 9;
        $GLOBALS['missing213'] = 7;
        echo 'H', func_num_args(), ';';
    };
}
function sink213(&$prior, $box) {
    echo 'S', func_num_args(), ':', $prior, ':', $box[0] === null ? 'N' : 'V', ';';
    $prior = 5;
}
$right213 = 8;
set_error_handler(HandlerCache213::H, 2);
sink213(Prior213::get(), [true ? $missing213 : $right213]);
echo Prior213::$value, ':', $missing213, ':', get_error_handler() === HandlerCache213::H ? '1' : '0';

restore_error_handler();
