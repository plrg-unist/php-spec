<?php
set_error_handler(function ($level, $message, $file, $line) {
    echo "H:" . $message . ":" . $line . "|";
    ini_set('include_path', 'required-live');
    return true;
});
try {
    require_once 'required-missing.php';
} catch (Error $error) {
    echo 'M:' . $error->getMessage() . ':' . $error->getLine() . '|';
}
restore_error_handler();
echo 'P:' . ini_get('include_path') . '|END';
