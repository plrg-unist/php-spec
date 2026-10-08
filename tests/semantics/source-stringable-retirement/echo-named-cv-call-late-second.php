<?php
class OperandEchoNamed {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-named-cv-call-late-second-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-named-cv-call-late-second-child.php' ? 'child' : 'main'), '|';
        function callEchoNamed($prefix = 'P', $sent = 'fallback') { echo 'PREFIX:', $prefix, '|SENT:', ($sent === null ? 'NULL' : $sent), '|'; return new ReturnedEchoNamed(); }
        $GLOBALS['argumentEchoNamed'] = 'LIVE'; echo 'INSTALL|';
    }
}
class ReturnedEchoNamed {
    public function __toString(): string { $e = new Exception('cast'); $trace = $e->getTrace(); echo 'TEXT:', $trace[0]['line'], '|'; unset($GLOBALS['argumentEchoNamed']); return 'BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $trace = $e->getTrace(); echo 'RESULT-D:', $trace[0]['line'], '|'; }
}
$value = include new OperandEchoNamed(); echo 'V:', $value, '|END';
