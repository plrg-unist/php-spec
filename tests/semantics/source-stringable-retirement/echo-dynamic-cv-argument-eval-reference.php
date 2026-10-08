<?php
class ReturnedDynamicReference {
    public function __toString(): string { $e = new Exception('text'); $t = $e->getTrace(); echo 'REF-TEXT:', $t[0]['line'], '|'; $GLOBALS['argumentDynamic'] = 'AFTER-CAST'; $GLOBALS['calleeDynamicArgument'] = 'AFTER-CALLEE'; return 'REF-BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'REF-D:', $t[0]['line'], '|'; }
}
function &selectedDynamicArgument(&$value) { $e = new Exception('call'); $t = $e->getTrace(); echo 'REF-CALL:', $t[0]['line'], ':', ($value === null ? 'NULL' : 'WRONG'), '|'; $value = 'AFTER-SEND'; $result = new ReturnedDynamicReference(); return $result; }
class OperandDynamicArgument {
    public function __toString(): string { echo 'CAST|'; return "\n\n\necho (\n    \$calleeDynamicArgument\n)\n(\n\n    \$argumentDynamic\n);\necho 'BODY|';\nreturn 97;\n"; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], ':eval|'; $GLOBALS['calleeDynamicArgument'] = 'selectedDynamicArgument'; unset($GLOBALS['argumentDynamic']); }
}
$value = eval(new OperandDynamicArgument()); echo 'V:', $value, '|LIVE:', $argumentDynamic, '|END';
