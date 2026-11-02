<?php
class RetvalEchoOB07 {
    public function __destruct() {
        echo "R1|R2|";
    }
}
set_error_handler(static function ($level, $message) {
    echo "H:", $level, "|";
    return new RetvalEchoOB07;
});
class LateRetvalEchoOB07 {
    public function __destruct() {
        echo "D1|";
        echo ob_start() ? "DT|" : "DF|";
        echo "D2|";
    }
}
ob_start(function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new LateRetvalEchoOB07);
    return "F" . $bytes;
});
echo "X|";
