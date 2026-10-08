<?php
class OperandEchoDynamic {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-call-invoke-result-throw-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; $GLOBALS['calleeEchoDynamic'] = new InvokerEchoDynamic(); }
}
class InvokerEchoDynamic {
    public function __invoke() { $e = new Exception('invoke'); $t = $e->getTrace(); echo 'INVOKE:', $t[0]['line'], '|'; unset($GLOBALS['calleeEchoDynamic']); return new ReturnedEchoDynamic(); }
    public function __destruct() { $e = new Exception('invoker'); $t = $e->getTrace(); echo 'INVOKER-D:', $t[0]['line'], '|'; }
}
class ReturnedEchoDynamic {
    public function __toString(): string { $e = new Exception('text'); $t = $e->getTrace(); echo 'TEXT:', $t[0]['line'], '|'; return 'BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'RESULT-D:', $t[0]['line'], '|'; throw new Exception('result-stop'); }
}
try { include new OperandEchoDynamic(); } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), '|'; }
echo 'END';
