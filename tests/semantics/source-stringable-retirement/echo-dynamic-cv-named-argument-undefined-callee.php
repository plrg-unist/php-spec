<?php
class OperandDynamicNamed {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-named-argument-undefined-callee-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; unset($GLOBALS['calleeDynamicNamed']); unset($GLOBALS['argumentDynamicNamed']); }
}
function selectedDynamicNamed($value) { echo 'WRONG-CALL|'; return 'WRONG-BYTES|'; }
set_error_handler(function($no, $message, $file, $line) { echo 'W:', $message, ':', $line, '|'; $GLOBALS['calleeDynamicNamed'] = 'selectedDynamicNamed'; $GLOBALS['argumentDynamicNamed'] = 'HANDLER'; return true; });
try { include new OperandDynamicNamed(); } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), ':', $e->getLine(), '|'; }
echo 'END';
