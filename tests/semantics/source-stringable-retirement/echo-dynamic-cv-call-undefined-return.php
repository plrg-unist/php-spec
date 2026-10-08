<?php
class OperandEchoDynamic {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-call-undefined-return-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; unset($GLOBALS['calleeEchoDynamic']); }
}
function selectedEchoDynamic() { echo 'WRONG-CALL|'; return 'WRONG-BYTES|'; }
set_error_handler(function ($level, $message, $file, $line) { echo 'W:', $message, ':', $line, '|'; $GLOBALS['calleeEchoDynamic'] = 'selectedEchoDynamic'; return true; });
$calleeEchoDynamic = 'selectedEchoDynamic';
try { include new OperandEchoDynamic(); } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), ':', $e->getLine(), '|'; }
echo 'LIVE:', $calleeEchoDynamic, '|END';
