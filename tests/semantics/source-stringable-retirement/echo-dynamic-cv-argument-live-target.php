<?php
class OperandDynamicArgument {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-argument-live-target-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|';
        function selectedDynamicArgument($value) { $e = new Exception('call'); $t = $e->getTrace(); echo 'CALL:', $t[0]['line'], ':', $value, '|'; $GLOBALS['calleeDynamicArgument'] = 'wrongDynamicArgument'; $GLOBALS['argumentDynamic'] = 'AFTER-SEND'; return new ReturnedDynamicArgument(); }
        $GLOBALS['calleeDynamicArgument'] = 'selectedDynamicArgument'; $GLOBALS['argumentDynamic'] = 'LIVE'; echo 'INSTALL|';
    }
}
class ReturnedDynamicArgument {
    public function __toString(): string { $e = new Exception('cast'); $t = $e->getTrace(); echo 'TEXT:', $t[0]['line'], '|'; unset($GLOBALS['calleeDynamicArgument']); unset($GLOBALS['argumentDynamic']); return 'BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'RESULT-D:', $t[0]['line'], '|'; }
}
function wrongDynamicArgument($value) { echo 'WRONG|'; return 'WRONG-BYTES|'; }
$calleeDynamicArgument = 'wrongDynamicArgument';
$value = include new OperandDynamicArgument(); echo 'V:', $value, '|END';
