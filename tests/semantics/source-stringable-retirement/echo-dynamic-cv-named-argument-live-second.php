<?php
class OperandDynamicNamed {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-named-argument-live-second-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|';
        function selectedDynamicNamed($prefix = 'P', $sent = 'D') { $e = new Exception('call'); $t = $e->getTrace(); echo 'CALL:', $t[0]['line'], ':', $prefix, ':', $sent, '|'; $GLOBALS['calleeDynamicNamed'] = 'wrongDynamicNamed'; $GLOBALS['argumentDynamicNamed'] = 'AFTER-SEND'; return new ReturnedDynamicNamed(); }
        $GLOBALS['calleeDynamicNamed'] = 'selectedDynamicNamed'; $GLOBALS['argumentDynamicNamed'] = 'LIVE'; echo 'INSTALL|';
    }
}
class ReturnedDynamicNamed {
    public function __toString(): string { $e = new Exception('cast'); $t = $e->getTrace(); echo 'TEXT:', $t[0]['line'], '|'; unset($GLOBALS['calleeDynamicNamed']); unset($GLOBALS['argumentDynamicNamed']); return 'BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'RESULT-D:', $t[0]['line'], '|'; }
}
function wrongDynamicNamed($value) { echo 'WRONG|'; return 'WRONG-BYTES|'; }
$calleeDynamicNamed = 'wrongDynamicNamed';
$value = include new OperandDynamicNamed(); echo 'V:', $value, '|END';
