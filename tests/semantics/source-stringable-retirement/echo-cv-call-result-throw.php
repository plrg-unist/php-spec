<?php
class Operand365 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-cv-call-result-throw-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-cv-call-result-throw-child.php' ? 'child' : 'main'), '|';
        $GLOBALS['argument365'] = 'LIVE'; echo 'REPLACE|';
    }
}
class Returned365 {
    public function __toString(): string { echo 'TEXT|'; unset($GLOBALS['argument365']); return 'BYTES|'; }
    public function __destruct() { echo 'RESULT-D|'; throw new Exception('result'); }
}
function call365($value) { echo 'CALL:', $value, '|'; return new Returned365(); }
$argument365 = 'OLD';
try { include new Operand365(); } catch (Exception $e) { echo 'CAUGHT:', $e->getMessage(), '|'; } echo 'END';
