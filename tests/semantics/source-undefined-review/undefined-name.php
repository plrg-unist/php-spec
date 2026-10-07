<?php
function cvReviewMissingName($level, $message, $file, $line) {
    echo 'H:', $message, ':', $line, '|';
    throw new Exception('missing-name');
}
set_error_handler('cvReviewMissingName', E_WARNING);
try { eval(${$missingName}); }
catch (Exception $e) { echo 'E:', $e->getMessage(), '|'; }
restore_error_handler();
echo 'END';
