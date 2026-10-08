<?php
class Operand353 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/dim-direct-live-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/dim-direct-live-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/dim-direct-live-child.php' ? 'filename' : 'none'), '|';
        $GLOBALS['rows353'] = ['live' => 'LIVE']; $GLOBALS['key353'] = 'live'; echo 'WRITE|';
    }
}
$rows353 = ['before' => 'WRONG']; $key353 = 'before';
$value = include new Operand353;
echo 'V:', $value, '|K:', $key353, '|END';
