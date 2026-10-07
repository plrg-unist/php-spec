<?php
class DeferredRegularSource {
    public function __toString(): string {
        echo 'T|';
        return __DIR__ . '/deferred-regular-multiline.php';
    }
    public function __destruct() {
        nativeDeferredRegularFunction(); echo "D:registered|";
        $error = new Exception('deferred');
        foreach ($error->getTrace() as $frame) {
            echo 'F:', $frame['function'], ':', $frame['line'], ':', ($frame['file'] === __FILE__ ? 'main' : ($frame['file'] === __DIR__ . '/deferred-regular-multiline.php' ? 'child' : 'other')), ':';
            if (isset($frame['args'][0])) { echo 'ARG:', ($frame['args'][0] === $this ? 'object' : ($frame['args'][0] === __FILE__ ? 'main' : ($frame['args'][0] === __DIR__ . '/deferred-regular-multiline.php' ? 'child' : 'other'))); }
            else { echo 'NOARG'; }
            echo '|';
        }
        throw $error;
    }
}
$value = 'old';
try {
    $value = include new DeferredRegularSource;
    echo 'A:', $value, '|';
    error_reporting(1);
    echo 'skipped|';
} catch (Throwable $error) {
    foreach ($error->getTrace() as $frame) { echo 'F:', $frame['function'], ':', $frame['line'], '|'; }
}
echo 'V:', $value, '|R:', error_reporting(), '|END';
