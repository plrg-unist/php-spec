<?php
class DeferredRegularSource {
    public function __toString(): string {
        echo 'T|';
        return __DIR__ . '/deferred-regular.php';
    }
    public function __destruct() {
        nativeDeferredRegularFunction(); echo "D:registered|";
        throw new Exception('deferred');
    }
}
$value = 'old';
try {
    $value = include new DeferredRegularSource;
    echo 'A:', $value, '|';
    error_reporting(1);
    echo 'skipped|';
} catch (Throwable $error) { echo 'C:', $error->getMessage(), '|'; }
echo 'V:', $value, '|R:', error_reporting(), '|END';
