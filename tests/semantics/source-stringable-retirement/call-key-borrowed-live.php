<?php
class Operand357 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/call-key-borrowed-live-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/call-key-borrowed-live-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/call-key-borrowed-live-child.php' ? 'filename' : 'none'), '|';
        $GLOBALS['rows357'] = ['chosen' => new Old357()]; echo 'RETIRE|';
    }
}
class Old357 { public function __destruct() { echo 'OLD|'; $GLOBALS['rows357'] = ['chosen' => 'CHILD-LIVE', 'wrong' => 'WRONG']; $GLOBALS['key357'] = 'wrong'; } }
function key357() { echo 'KEY|'; $GLOBALS['rows357'] = ['chosen' => 'CALL-LIVE']; echo 'RETURN|'; return 'chosen'; }
$key357 = 'before'; $value = include new Operand357(); echo 'V:', $value, '|K:', $key357, '|END';
