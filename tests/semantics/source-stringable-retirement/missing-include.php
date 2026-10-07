<?php
class HelperResultSource {
    public function __toString(): string { echo 'T|'; return __DIR__ . '/helper-missing-file.php'; }
    public function __destruct() { echo 'D|';
        $error = new Exception('deferred');
        foreach ($error->getTrace() as $frame) {
            echo 'F:', $frame['function'], ':', $frame['line'], ':', ($frame['file'] === __FILE__ ? 'main' : ($frame['file'] === __DIR__ . '/helper-missing-file.php' ? 'child' : 'other')), ':';
            if (isset($frame['args'][0])) { echo 'ARG:', ($frame['args'][0] === $this ? 'object' : ($frame['args'][0] === __FILE__ ? 'main' : ($frame['args'][0] === __DIR__ . '/helper-missing-file.php' ? 'child' : 'other'))); }
            else { echo 'NOARG'; }
            echo '|';
        }
        throw $error;
    }
}
$value = 'old';
try {
    $value = include new HelperResultSource;
    echo 'A:', ($value === false ? 'false' : ($value === true ? 'true' : ($value === null ? 'null' : $value))), '|';
    error_reporting(1);
    echo 'skipped|';
} catch (Throwable $error) { echo 'C:', $error->getMessage(), '|'; }
echo 'V:', ($value === false ? 'false' : ($value === true ? 'true' : ($value === null ? 'null' : $value))), '|R:', error_reporting(), '|END';
