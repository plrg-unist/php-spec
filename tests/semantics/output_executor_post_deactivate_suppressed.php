<?php
class LateSuppressedStartOB06 {
    public function __destruct() {
        echo "D1|";
        echo @ob_start() ? "T|" : "F|";
        echo ob_get_level(), "|D2|";
    }
}
ob_start(function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new LateSuppressedStartOB06);
    return "F" . $bytes;
});
echo "X|";
