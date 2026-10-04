<?php
set_error_handler(function ($level, $message, $file, $line) {
    echo 'H:' . $line . '|';
    throw new Exception('eval-warning');
});
try {
    eval('include "eval-warning-missing.php";');
} catch (Exception $e) {
    echo $e->getTraceAsString(), '|';
}
restore_error_handler();
echo 'END';
