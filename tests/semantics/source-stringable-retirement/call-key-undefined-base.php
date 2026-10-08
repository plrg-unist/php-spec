<?php
class Operand357 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/call-key-undefined-base-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/call-key-undefined-base-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/call-key-undefined-base-child.php' ? 'filename' : 'none'), '|';
        unset($GLOBALS['rows357']); echo 'RETIRE|';
    }
}
function key357() { echo 'KEY|'; $GLOBALS['rows357'] = ['chosen' => 'DEFINED-LIVE']; return 'chosen'; }
$value = include new Operand357(); echo 'V:', $value, '|END';
