<?php
class Operand361 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-call-cast-throw-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-call-cast-throw-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/echo-call-cast-throw-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|';
    }
}
class ThrowCast361 {
    public function __toString(): string { echo 'THROW-TEXT|'; throw new Exception('cast'); }
    public function __destruct() { echo 'THROW-D|'; throw new Exception('destroy'); }
}
function call361() { echo 'CALL|'; return new ThrowCast361(); }
try { include new Operand361(); } catch (Exception $e) { echo 'CAUGHT:', $e->getMessage(), ':', $e->getPrevious()->getMessage(), '|'; } echo 'END';
