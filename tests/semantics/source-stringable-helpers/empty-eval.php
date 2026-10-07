<?php
class HelperResultSource {
    public function __toString(): string { echo 'T|'; return ''; }
    public function __destruct() { echo 'D|'; throw new Exception('deferred'); }
}
$value = 'old';
try {
    $value = eval(new HelperResultSource);
    echo 'A:', ($value === false ? 'false' : ($value === true ? 'true' : ($value === null ? 'null' : $value))), '|';
    error_reporting(1);
    echo 'skipped|';
} catch (Throwable $error) { echo 'C:', $error->getMessage(), '|'; }
echo 'V:', ($value === false ? 'false' : ($value === true ? 'true' : ($value === null ? 'null' : $value))), '|R:', error_reporting(), '|END';
