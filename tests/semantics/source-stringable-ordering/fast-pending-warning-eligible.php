<?php
class FastPendingEligibleSource {
    public function __toString(): string {
        echo 'T|';
        return __DIR__ . '/deferred-compile-only.php';
    }
    public function __destruct() {
        nativeDeferredFastFunction(); echo 'D:registered|';
        throw new Exception('deferred');
    }
}
set_error_handler(function ($level, $message) { echo 'H:', $message, '|'; return true; }, E_USER_WARNING);
$value = 'old';
try {
    $value = include new FastPendingEligibleSource;
    echo 'A:', $value, '|';
    trigger_error('later', E_USER_WARNING);
    echo 'skipped|';
} catch (Throwable $error) { echo 'C:', $error->getMessage(), '|'; }
echo 'V:', $value, '|R:', error_reporting(), '|END';
