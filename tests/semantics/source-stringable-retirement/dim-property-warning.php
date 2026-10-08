<?php
class Operand353 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/dim-property-warning-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/dim-property-warning-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/dim-property-warning-child.php' ? 'filename' : 'none'), '|';
        $GLOBALS['rows353'] = ['' => new Target353, 'wrong' => new Wrong353]; echo 'WRITE|';
    }
}
class Target353 { public $value = 'before'; }
class Wrong353 { public $value = 'WRONG'; }
function warning353($c, $m, $f, $l) { echo 'W:', $l, ':', $m, '|'; $GLOBALS['key353'] = 'wrong'; $GLOBALS['rows353']['']->value = 'HANDLER-LIVE'; return true; }
set_error_handler('warning353');
$rows353 = ['' => new Wrong353];
$value = include new Operand353;
echo 'V:', $value, '|K:', $key353, '|END';
