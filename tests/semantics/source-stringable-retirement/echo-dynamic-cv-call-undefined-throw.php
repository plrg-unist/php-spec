<?php
class OperandEchoDynamic {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-call-undefined-throw-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; unset($GLOBALS['calleeEchoDynamic']); }
}
function selectedEchoDynamic() { echo 'WRONG-CALL|'; return 'WRONG-BYTES|'; }
set_error_handler(function ($level, $message, $file, $line) { echo 'W:', $message, ':', $line, '|'; $GLOBALS['calleeEchoDynamic'] = 'selectedEchoDynamic'; throw new Exception('handler-stop'); });
$calleeEchoDynamic = 'selectedEchoDynamic';
try { include new OperandEchoDynamic(); } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), '|'; }
echo 'LIVE:', $calleeEchoDynamic, '|END';
