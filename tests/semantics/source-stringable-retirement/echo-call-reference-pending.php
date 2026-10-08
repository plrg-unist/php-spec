<?php
class Operand361 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-call-reference-pending-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-call-reference-pending-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/echo-call-reference-pending-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|';
    }
}
class Pending361 {
    public function __toString(): string { echo 'PENDING-TEXT|'; $GLOBALS['ref361'] = new Later361(); unset($GLOBALS['ref361']); return 'PENDING-BYTES|'; }
    public function __destruct() { echo 'OLD-D|'; throw new Exception('old'); }
}
class Later361 { public function __destruct() { echo 'NEW-D|'; throw new Exception('new'); } }
function &call361() { echo 'REF-CALL|'; $value = new Pending361(); $GLOBALS['ref361'] =& $value; return $value; }
try { include new Operand361(); } catch (Exception $e) { echo 'CAUGHT:', $e->getMessage(), ':', $e->getPrevious()->getMessage(), '|'; } echo 'END';
