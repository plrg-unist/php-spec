<?php
class OperandDynamicArgument {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-argument-undefined-callee-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; unset($GLOBALS['calleeDynamicArgument']); unset($GLOBALS['argumentDynamic']); }
}
function selectedDynamicArgument($value) { echo 'WRONG-CALL|'; return 'WRONG-BYTES|'; }
set_error_handler(function($no, $message, $file, $line) { echo 'W:', $message, ':', $line, '|'; $GLOBALS['calleeDynamicArgument'] = 'selectedDynamicArgument'; $GLOBALS['argumentDynamic'] = 'HANDLER'; return true; });
try { include new OperandDynamicArgument(); } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), ':', $e->getLine(), '|'; }
echo 'END';
