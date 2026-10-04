<?php
register_shutdown_function(function () {
    echo 'Q:' . ini_get('include_path') . '|';
    ini_set('display_errors', '0');
});
set_error_handler(function ($level, $message, $file, $line) {
    echo 'H:' . $line . '|';
    ini_set('include_path', 'callback-path');
    ini_set('display_errors', 'stdout');
    include __DIR__ . '/compile-bad.php';
    echo 'UNREACHED';
    return false;
});
include 'shutdown-missing.php';
echo 'UNREACHED';
