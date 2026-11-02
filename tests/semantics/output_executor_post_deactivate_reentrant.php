<?php
set_error_handler(static function ($level, $message) {
    echo "H1|";
    echo ob_start() ? "INNER-T|" : "INNER-F|";
    return true;
});
class LateReentrantStartOB06 {
    public function __destruct() {
        echo "D1|";
        echo ob_start() ? "OUTER-T|" : "OUTER-F|";
        echo ob_get_level(), "|D2|";
    }
}
ob_start(function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new LateReentrantStartOB06);
    return "F" . $bytes;
});
echo "X|";
