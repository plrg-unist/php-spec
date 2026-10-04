<?php
set_error_handler(function ($level, $message, $file, $line) {
    echo "H:" . $message . ":" . $line . "|";
    exit('STOP');
});
include 'exit-missing.php';
echo 'UNREACHED';
