<?php
set_error_handler(function ($level, $message, $file, $line) {
    echo "H:" . $message . ":" . $line . "|";
    ini_set('include_path', 'thrown-path');
    throw new Exception('handler-stop');
});
try {
    require 'throw-missing.php';
} catch (Exception $error) {
    echo 'M:' . $error->getMessage() . '|' . $error->getTraceAsString() . '|';
}
try {
    include_once 'throw-again.php';
} catch (Exception $error) {
    echo 'I:' . $error->getMessage() . '|';
}
restore_error_handler();
echo 'P:' . ini_get('include_path') . '|END';
