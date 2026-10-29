<?php
declare(strict_types=1);
function weakDiagnosticOB01(string $level, string $message, string $file, int $line): bool {
    echo 'W|' . $level . '|' . $file . '|' . $line . '|';
    return true;
}
function typedDiagnosticFinalOB01(string $bytes, int $phase): string {
    echo 'discard|';
    return '[' . $bytes . ']';
}
set_error_handler('weakDiagnosticOB01');
ob_start('typedDiagnosticFinalOB01', 0);
echo 'x|';
