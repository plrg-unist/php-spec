<?php
set_error_handler(function($level, $message, $file, $line) {
    echo 'H:', $level, ':', $line, '|';
    ini_set('precision', '1tail');
    return true;
});
ini_set('precision', '3tail');
include __DIR__ . '/compiled-child.php';
echo 'END';
