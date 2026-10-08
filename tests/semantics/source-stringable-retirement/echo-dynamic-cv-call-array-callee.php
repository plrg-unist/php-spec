<?php
class OperandEchoDynamic {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-call-array-callee-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; $GLOBALS['calleeEchoDynamic'] = ['TargetEchoDynamic', 'run']; }
}
class TargetEchoDynamic {
    public static function run() { $e = new Exception('call'); $t = $e->getTrace(); echo 'ARRAY-CALL:', $t[0]['line'], '|'; $GLOBALS['calleeEchoDynamic'] = null; return 'ARRAY-BYTES|'; }
}
$value = include new OperandEchoDynamic(); echo 'V:', $value, '|END';
