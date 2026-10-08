<?php
class OperandCastDeclaration {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-call-cast-declaration-child.php'; }
    public function __destruct() { $e = new Exception('operand'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; $GLOBALS['calleeEchoDynamic'] = 'selectedCastDeclaration'; }
}
class ReturnedCastDeclaration {
    public function __toString(): string { $e = new Exception('text'); $t = $e->getTrace(); echo 'TEXT:', $t[0]['line'], '|'; function installedDuringCast() { echo 'INSTALLED|'; return 'LATER|'; } return 'BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $t = $e->getTrace(); echo 'RESULT-D:', $t[0]['line'], '|'; }
}
function selectedCastDeclaration() { echo 'SELECTED|'; return new ReturnedCastDeclaration(); }
$value = include new OperandCastDeclaration(); echo 'V:', $value, '|';
$again = eval('return 3;'); echo 'AGAIN:', $again, '|END';
