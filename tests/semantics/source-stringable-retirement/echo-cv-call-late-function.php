<?php
class Operand365 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-cv-call-late-function-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-cv-call-late-function-child.php' ? 'child' : 'main'), '|';
        function call365($value) { echo 'CALL:', $value, '|'; return 'RESULT|'; } $GLOBALS['argument365'] = 'LIVE'; echo 'INSTALL|';
    }
}
$value = include new Operand365(); echo 'V:', $value, '|A:', $argument365, '|END';
