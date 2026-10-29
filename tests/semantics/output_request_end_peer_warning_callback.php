<?php
function warningOB01(int $severity, string $message): bool {
    echo 'W:', $severity, ':', $message, '|';
    return true;
}
function finalWarningOB01(string $bytes, int $phase): string {
    echo 'H:', $phase, '|';
    trigger_error('from-final-handler', E_USER_WARNING);
    return '[' . $bytes . ']';
}
set_error_handler('warningOB01');
ob_start('finalWarningOB01', 0);
echo 'x';
