<?php
class CallArgumentTarget333 { public $value = 'before'; }
class CallArgumentOperand333 {
    public function __toString(): string { global $target333, $arg333; echo 'cast|'; $target333->value = 'cast'; $arg333 = 'cast333'; return __DIR__ . '/call-argument-property-nonthrow-child.php'; }
    public function __destruct() {
        global $target333;
        source_argument_ready_333();
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'READY:', $target333->value, '|';
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/call-argument-property-nonthrow-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/call-argument-property-nonthrow-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|';
    }
}
function source_argument_warning_333($code, $message, $file, $line) { echo 'W:', $line, ':', $message, '|'; return true; }
set_error_handler('source_argument_warning_333');
$target333 = new CallArgumentTarget333; $arg333 = 'unused333';
$value = 'before';
try {
    $value = include new CallArgumentOperand333;
    echo 'AFTER-BODY|';
} catch (Throwable $error) { echo 'caught|'; }
echo 'A:', (isset($arg333) ? $arg333 : 'missing'), '|T:', $target333->value, '|V:', $value, '|H:', (isset($missing333) ? $missing333 : 'none'), '|END';
