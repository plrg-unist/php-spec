<?php
class Operand357 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/call-key-missing-key-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/call-key-missing-key-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/call-key-missing-key-child.php' ? 'filename' : 'none'), '|';
        $GLOBALS['rows357'] = ['old' => new Old357()]; echo 'RETIRE|';
    }
}
class Old357 { public function __destruct() { echo 'OLD|'; } }
function key357() { echo 'KEY|'; return 'absent'; }
function warning357($level, $message, $file, $line) { echo 'W:', $line, ':', $message, '|'; $GLOBALS['rows357'] = ['absent' => 'WRONG']; echo 'HANDLER|'; return true; }
set_error_handler('warning357'); $value = include new Operand357(); echo 'V:', $value, '|END';
