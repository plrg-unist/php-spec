<?php
class ReturnedDynamicNamedReference {
    public function __toString(): string { $e = new Exception('text'); $t = $e->getTrace(); echo 'REF-TEXT:', $t[0]['line'], '|'; $GLOBALS['argumentDynamicNamed'] = 'AFTER-CAST'; $GLOBALS['calleeDynamicNamed'] = 'AFTER-CALLEE'; return 'REF-BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'REF-D:', $t[0]['line'], '|'; }
}
function &selectedDynamicNamed($prefix = 'P', &$sent = null) { $e = new Exception('call'); $t = $e->getTrace(); echo 'REF-CALL:', $t[0]['line'], ':', $prefix, ':', ($sent === null ? 'NULL' : 'WRONG'), '|'; $sent = 'AFTER-SEND'; $result = new ReturnedDynamicNamedReference(); return $result; }
class OperandDynamicNamed {
    public function __toString(): string { echo 'CAST|'; return "\n\n\necho (\n    \$calleeDynamicNamed\n)\n(\n\n    sent:\n\n    \$argumentDynamicNamed\n);\necho 'BODY|';\nreturn 97;\n"; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], ':eval|'; $GLOBALS['calleeDynamicNamed'] = 'selectedDynamicNamed'; unset($GLOBALS['argumentDynamicNamed']); }
}
$value = eval(new OperandDynamicNamed()); echo 'V:', $value, '|LIVE:', $argumentDynamicNamed, '|END';
