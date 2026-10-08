<?php
class Target350 { public $value = 'before'; }
function warning350($c, $m, $f, $l) { echo 'W:', $l, ':', $m, '|'; $GLOBALS['Array']->value = 'LIVE'; $GLOBALS['name350'] = 'other350'; return true; }
class Operand350 {
    public function __toString(): string { echo 'OPERANDCAST|'; return __DIR__ . '/array-name-retirement-child.php'; }
    public function __destruct() {
        $e = new Exception('retirement'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/array-name-retirement-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/array-name-retirement-child.php' ? 'filename' : 'none'), '|RETIRE|';
    }
}
set_error_handler('warning350');
$Array = new Target350; $name350 = [];
$value = include new Operand350;
echo 'V:', $value, '|T:', $Array->value, '|END';
