<?php
class MissingNameTarget339 { public $value = 'before'; }
class MissingNameOperand339 {
    public function __toString(): string { echo 'cast|'; return __DIR__ . '/missing-name-cv-retirement-child.php'; }
    public function __destruct() {
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/missing-name-cv-retirement-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/missing-name-cv-retirement-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|';
    }
}
function warning339($code, $message, $file, $line) { global $missing339, $target339; echo 'W:', $line, ':', $message, '|'; $missing339 = 'target339'; $target339->value = 'LIVE'; return true; }
set_error_handler('warning339');
$target339 = new MissingNameTarget339;
$value = 'before';
$value = include new MissingNameOperand339;
echo 'V:', $value, '|N:', $missing339, '|T:', $target339->value, '|END';
