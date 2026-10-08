<?php
class Operand361 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-call-reference-live-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-call-reference-live-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/echo-call-reference-live-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|';
    }
}
class Mutable361 {
    public function __toString(): string { echo 'MUT-TEXT|'; $GLOBALS['ref361'] = new Later361(); unset($GLOBALS['ref361']); return 'MUT-BYTES|'; }
    public function __destruct() { echo 'OLD-D|'; }
}
class Later361 { public function __destruct() { echo 'NEW-D|'; } }
class Plain361 {
    public function __toString(): string { echo 'PLAIN-TEXT|'; return 'PLAIN-BYTES|'; }
    public function __destruct() { echo 'PLAIN-D|'; }
}
class RefThrow361 {
    public function __toString(): string { echo 'REF-THROW-TEXT|'; throw new Exception('ref-cast'); }
    public function __destruct() { echo 'REF-THROW-D|'; }
}
function &call361() { echo 'REF-CALL|'; $value = new Mutable361(); $GLOBALS['ref361'] =& $value; return $value; }
function &plain361() { $value = new Plain361(); return $value; }
function &throwing361() { $value = new RefThrow361(); return $value; }
try { include new Operand361(); } catch (Exception $e) { echo 'CAUGHT:', $e->getMessage(), '|'; } echo 'END';
