<?php
class Operand365 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-cv-call-result-lines-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-cv-call-result-lines-child.php' ? 'child' : 'main'), '|';
        $GLOBALS['argument365'] = 'LIVE'; echo 'REPLACE|';
    }
}
class Returned365 {
    public function __toString(): string { $e = new Exception('cast'); $trace = $e->getTrace(); echo 'TEXT:', $trace[0]['line'], '|'; unset($GLOBALS['argument365']); return 'BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $trace = $e->getTrace(); echo 'RESULT-D:', $trace[0]['line'], '|'; }
}
function call365($value) { echo 'CALL:', $value, '|'; return new Returned365(); }
$argument365 = 'OLD';
$value = include new Operand365(); echo 'V:', $value, '|END';
