<?php
class LateUnknownStartOB11 {
    public function __destruct() {
        echo "D1|";
        echo ob_start("MissingClassOB11::run") ? "T|" : "F|";
        echo ob_get_level(), "|D2|";
    }
}
ob_start(function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new LateUnknownStartOB11);
    return "F" . $bytes;
});
echo "X|";
