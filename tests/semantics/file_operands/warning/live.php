<?php
class WarningOperand {
    public function __toString(): string {
        echo "CONVERT|";
        ini_set('include_path', 'provider-path');
        return 'warning-missing.php';
    }
}
$stage = 0;
set_error_handler(function ($level, $message, $file, $line) use (&$stage) {
    ++$stage;
    echo "H" . $stage . ":" . $message . ":" . $line . "|";
    if ($stage === 1) {
        ini_set('include_path', 'after-first');
        ini_set('display_errors', 'stdout');
        echo "N:" . (include 'nested-target.php') . "|";
    } else {
        ini_set('include_path', 'after-second');
        ini_set('display_errors', 'stderr');
    }
    return false;
});
$result = include new WarningOperand;
restore_error_handler();
echo "R:" . (int)$result . ':' . ini_get('include_path') . '|END';
