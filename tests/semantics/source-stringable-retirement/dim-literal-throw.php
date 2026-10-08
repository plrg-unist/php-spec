<?php
class Operand353 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/dim-literal-throw-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/dim-literal-throw-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/dim-literal-throw-child.php' ? 'filename' : 'none'), '|';
        echo 'THROW|'; throw $e;
    }
}
function warning353($c, $m, $f, $l) { echo 'WARN-BAD:', $l, ':', $m, '|'; throw new Exception('late'); }
set_error_handler('warning353');
try { $value = include new Operand353; echo 'BAD|'; } catch (Throwable $e) { echo 'CAUGHT:', $e->getMessage(), '|'; }
echo 'END';
