<?php
error_reporting(0);
class WarningBorrowStatic13 {
    public private(set) static ?int $value = null;
    public static function attach(&$value) {
        self::$value =& $value;
    }
    public static function put($value) {
        self::$value = $value;
        echo func_num_args(), ';';
    }
}
$x = null;
$a =& $x;
WarningBorrowStatic13::attach($x);
function warningBorrowSetter13($severity, $message, $file, $line) {
    WarningBorrowStatic13::put(9);
}
set_error_handler('warningBorrowSetter13', 2);
echo ($a === $missing_allowed ? 1 : 0), ':', $a, ':', WarningBorrowStatic13::$value, ';';
restore_error_handler();
$denied = function($severity, $message, $file, $line) {
    $slot =& WarningBorrowStatic13::$value;
};
set_error_handler($denied, 2);
try {
    echo ($a !== $missing_denied ? 1 : 0), 'bad';
} catch (Error $e) {
    echo 'blocked:', $a, ':', (get_error_handler() === $denied ? 1 : 0);
}
restore_error_handler();
