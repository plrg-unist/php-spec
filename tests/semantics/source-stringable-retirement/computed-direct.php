<?php
class ComputedTarget327 { public $value = 'before'; }
class ComputedOperand327 {
    public function __toString(): string { global $target327; echo 'cast|'; $target327 = 'cast'; return __DIR__ . '/computed-direct-child.php'; }
    public function __destruct() {
        global $target327;
        source_computed_ready_327();
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'READY:', $target327, '|';
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/computed-direct-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/computed-direct-child.php' ? 'filename' : 'none'), '|';
        throw $error;
    }
}
function source_computed_warning_327($code, $message, $file, $line) { echo 'W:', $line, ':', $message, '|'; return true; }
set_error_handler('source_computed_warning_327');
$target327 = 'before';
$value = 'before';
try {
    $value = include new ComputedOperand327;
    echo 'AFTER-BODY|';
} catch (Throwable $error) { echo 'caught|'; }
echo 'T:', $target327, '|V:', $value, '|END';
