<?php
class FastPendingValueSource {
    public function __toString(): string {
        echo 'T|';
        return __DIR__ . '/deferred-compile-only.php';
    }
    public function __destruct() {
        nativeDeferredFastFunction(); echo 'D:registered|';
        throw new Exception('deferred');
    }
}
$value = 'old';
try {
    $value = include new FastPendingValueSource;
    echo 'A:', $value, '|';
    trigger_error('later', E_WARNING);
    echo 'skipped|';
} catch (Throwable $error) {
    echo 'C:', ($error instanceof ValueError ? 'ValueError' : 'Exception'), ':', $error->getMessage(), '|';
    $previous = $error->getPrevious();
    echo 'P:', ($previous === null ? '-' : $previous->getMessage()), '|';
}
echo 'V:', $value, '|R:', error_reporting(), '|END';
