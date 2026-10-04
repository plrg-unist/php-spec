<?php
set_error_handler(function ($level, $message, $file, $line) {
    echo "H:" . $message . ":" . $line . "|";
    ini_set('display_errors', '0');
    trigger_error('handler-fatal', E_USER_ERROR);
    echo 'UNREACHED';
});
include 'fatal-missing.php';
echo 'UNREACHED';
