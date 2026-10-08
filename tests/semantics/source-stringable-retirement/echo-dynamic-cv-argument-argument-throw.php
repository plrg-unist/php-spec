<?php
class OperandDynamicArgument {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-argument-argument-throw-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; $GLOBALS['calleeDynamicArgument'] = new InvokerDynamicArgument(); unset($GLOBALS['argumentDynamic']); }
}
class InvokerDynamicArgument {
    public function __invoke($value) { $e = new Exception('invoke'); $t = $e->getTrace(); echo 'INVOKE:', $t[0]['line'], ':', ($value === null ? 'NULL' : 'WRONG'), '|'; return new ReturnedDynamicArgument(); }
    public function __destruct() { $e = new Exception('invoker'); $t = $e->getTrace(); echo 'INVOKER-D:', $t[0]['line'], '|'; }
}
class ReturnedDynamicArgument {
    public function __toString(): string { $e = new Exception('cast'); $t = $e->getTrace(); echo 'TEXT:', $t[0]['line'], '|'; unset($GLOBALS['calleeDynamicArgument']); unset($GLOBALS['argumentDynamic']); return 'BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'RESULT-D:', $t[0]['line'], '|'; }
}
function wrongDynamicArgument($value) { echo 'WRONG|'; return 'WRONG-BYTES|'; }
set_error_handler(function($no, $message, $file, $line) { echo 'W:', $message, ':', $line, '|'; unset($GLOBALS['calleeDynamicArgument']); $GLOBALS['calleeDynamicArgument'] = 'wrongDynamicArgument'; $GLOBALS['argumentDynamic'] = 'HANDLER'; throw new Exception('handler-stop'); });
try { $value = include new OperandDynamicArgument(); echo 'V:', $value, '|'; } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), '|'; }
echo 'LIVE:', $argumentDynamic, '|END';
