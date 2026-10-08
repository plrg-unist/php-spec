<?php
class ReturnedEchoDynamic {
    public function __toString(): string { $e = new Exception('text'); $t = $e->getTrace(); echo 'REF-TEXT:', $t[0]['line'], '|'; $GLOBALS['calleeEchoDynamic'] = 'AFTER-CAST'; return 'REF-BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'REF-D:', $t[0]['line'], '|'; }
}
function &selectedEchoDynamic() { echo 'REF-CALL|'; $result = new ReturnedEchoDynamic(); return $result; }
class OperandEchoDynamic {
    public function __toString(): string { echo 'CAST|'; return "\n\n\necho (\n    \$calleeEchoDynamic\n)\n(\n);\necho 'BODY|';\nreturn 97;"; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], ':eval|'; $GLOBALS['calleeEchoDynamic'] = 'selectedEchoDynamic'; }
}
$value = eval(new OperandEchoDynamic()); echo 'V:', $value, '|LIVE:', $calleeEchoDynamic, '|END';
