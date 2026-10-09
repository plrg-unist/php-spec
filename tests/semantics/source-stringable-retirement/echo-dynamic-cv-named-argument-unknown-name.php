<?php
class OperandDynamicNamed {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-named-argument-unknown-name-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; }
}
class InvokerDynamicNamed {
    public function __invoke($prefix = 'P', $sent = 'D') { echo 'WRONG-INVOKE|'; return 'WRONG|'; }
    public function __destruct() { $e = new Exception('invoker'); $t = $e->getTrace(); echo 'INVOKER-D:', $t[0]['line'], '|'; }
}
function runDynamicNamed() { $calleeDynamicNamed = new InvokerDynamicNamed(); return include new OperandDynamicNamed(); }
set_error_handler(function($no, $message, $file, $line) { echo 'W:', $message, ':', $line, '|'; return true; });
try { runDynamicNamed(); } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), ':', $e->getLine(), '|'; }
echo 'END';
