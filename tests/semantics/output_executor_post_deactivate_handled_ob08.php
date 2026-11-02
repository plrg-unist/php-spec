<?php
set_error_handler(static function ($level, $message) {
    echo "H:", $level, "|";
    return true;
});
class LateHandledStartOB08 {
    public function __destruct() {
        echo "D1|";
        echo ob_start(null) ? "T|" : "F|";
        echo ob_get_level(), "|D2|";
    }
}
ob_start(function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new LateHandledStartOB08);
    return "F" . $bytes;
});
echo "X|";
