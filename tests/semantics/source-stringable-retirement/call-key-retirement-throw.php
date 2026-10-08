<?php
class Operand357 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/call-key-retirement-throw-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/call-key-retirement-throw-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/call-key-retirement-throw-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|'; throw new Exception('retire');
    }
}
function key357() { echo 'KEY-BAD|'; return 'chosen'; }
try { $value = include new Operand357(); echo 'AFTER-BAD|'; } catch (Throwable $e) { echo 'CAUGHT:', $e->getMessage(), '|'; } echo 'END';
