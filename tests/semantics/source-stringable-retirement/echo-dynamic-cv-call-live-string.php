<?php
class OperandEchoDynamic {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-call-live-string-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $t = $e->getTrace();
        echo 'D:', $t[0]['line'], ':', ($t[0]['file'] === __DIR__ . '/echo-dynamic-cv-call-live-string-child.php' ? 'child' : 'main'), '|';
        function selectedEchoDynamic() { echo 'SELECTED|'; $GLOBALS['calleeEchoDynamic'] = 'wrongEchoDynamic'; return new ReturnedEchoDynamic(); }
        $GLOBALS['calleeEchoDynamic'] = 'selectedEchoDynamic'; echo 'INSTALL|';
    }
}
class ReturnedEchoDynamic {
    public function __toString(): string { $e = new Exception('text'); $t = $e->getTrace(); echo 'TEXT:', $t[0]['line'], '|'; unset($GLOBALS['calleeEchoDynamic']); return 'BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'RESULT-D:', $t[0]['line'], '|'; }
}
function wrongEchoDynamic() { echo 'WRONG|'; return 'WRONG-BYTES|'; }
$calleeEchoDynamic = 'wrongEchoDynamic';
$value = include new OperandEchoDynamic(); echo 'V:', $value, '|END';
