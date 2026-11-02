<?php
class RetvalStartOB06 {
    public function __destruct() {
        echo "R1|";
        echo ob_start() ? "RT|" : "RF|";
        echo "R2|";
    }
}
set_error_handler(static function ($level, $message) {
    echo "H:", $level, "|";
    return new RetvalStartOB06;
});
class LateRetvalStartOB06 {
    public function __destruct() {
        echo "D1|";
        echo ob_start() ? "DT|" : "DF|";
        echo "D2|";
    }
}
ob_start(function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new LateRetvalStartOB06);
    return "F" . $bytes;
});
echo "X|";
