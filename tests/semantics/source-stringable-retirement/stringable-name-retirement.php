<?php
class Target343 { public $value = 'before'; }
class Name343 { public function __toString(): string { global $target343; echo 'NAMECAST|'; $target343->value = 'LIVE'; return 'target343'; } }
class Operand343 {
    public function __toString(): string { echo 'OPERANDCAST|'; return __DIR__ . '/stringable-name-retirement-child.php'; }
    public function __destruct() {
        $e = new Exception('retirement'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/stringable-name-retirement-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/stringable-name-retirement-child.php' ? 'filename' : 'none'), '|RETIRE|';
    }
}
$target343 = new Target343; $name343 = new Name343;
$value = include new Operand343;
echo 'V:', $value, '|T:', $target343->value, '|END';
