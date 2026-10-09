<?php
class OperandDynamicNamed {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-named-argument-warning-return-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; $GLOBALS['calleeDynamicNamed'] = new InvokerDynamicNamed(); unset($GLOBALS['argumentDynamicNamed']); }
}
class InvokerDynamicNamed {
    public function __invoke($prefix = 'P', $sent = 'D') { $e = new Exception('invoke'); $t = $e->getTrace(); echo 'INVOKE:', $t[0]['line'], ':', $prefix, ':', ($sent === null ? 'NULL' : 'WRONG'), '|'; return new ReturnedDynamicNamed(); }
    public function __destruct() { $e = new Exception('invoker'); $t = $e->getTrace(); echo 'INVOKER-D:', $t[0]['line'], '|'; }
}
class ReturnedDynamicNamed {
    public function __toString(): string { $e = new Exception('cast'); $t = $e->getTrace(); echo 'TEXT:', $t[0]['line'], '|'; unset($GLOBALS['calleeDynamicNamed']); unset($GLOBALS['argumentDynamicNamed']); return 'BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'RESULT-D:', $t[0]['line'], '|'; }
}
function wrongDynamicNamed($value) { echo 'WRONG|'; return 'WRONG-BYTES|'; }
set_error_handler(function($no, $message, $file, $line) { echo 'W:', $message, ':', $line, '|'; unset($GLOBALS['calleeDynamicNamed']); $GLOBALS['calleeDynamicNamed'] = 'wrongDynamicNamed'; $GLOBALS['argumentDynamicNamed'] = 'HANDLER'; return true; });
try { $value = include new OperandDynamicNamed(); echo 'V:', $value, '|'; } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), '|'; }
echo 'END';
