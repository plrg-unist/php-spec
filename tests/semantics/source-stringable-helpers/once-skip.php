<?php
class HelperResultSource {
    public function __toString(): string { echo 'T|'; return __DIR__ . '/helper-skip-body.php'; }
    public function __destruct() { echo 'D|'; throw new Exception('deferred'); }
}
include_once __DIR__ . '/helper-skip-body.php';
$value = 'old';
try {
    $value = include_once new HelperResultSource;
    echo 'A:', ($value === false ? 'false' : ($value === true ? 'true' : ($value === null ? 'null' : $value))), '|';
    error_reporting(1);
    echo 'skipped|';
} catch (Throwable $error) { echo 'C:', $error->getMessage(), '|'; }
echo 'V:', ($value === false ? 'false' : ($value === true ? 'true' : ($value === null ? 'null' : $value))), '|R:', error_reporting(), '|END';
