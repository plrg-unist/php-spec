<?php
class NamedArgumentTarget336 { public $value = 'before'; }
class NamedArgumentOperand336 {
    public function __toString(): string { global $target336, $arg336; echo 'cast|'; $target336 = 'cast'; $arg336 = 'cast336'; return __DIR__ . '/named-argument-direct-child.php'; }
    public function __destruct() {
        global $target336;
        source_named_ready_336();
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'READY:', $target336, '|';
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/named-argument-direct-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/named-argument-direct-child.php' ? 'filename' : 'none'), '|';
        throw $error;
    }
}
function source_named_warning_336($code, $message, $file, $line) { echo 'W:', $line, ':', $message, '|'; return true; }
set_error_handler('source_named_warning_336');
$target336 = 'before'; $arg336 = 'unused336';
$value = 'before';
try {
    $value = include new NamedArgumentOperand336;
    echo 'AFTER-BODY|';
} catch (Throwable $error) { echo 'caught|'; }
echo 'A:', (isset($arg336) ? $arg336 : 'missing'), '|T:', $target336, '|V:', $value, '|H:', (isset($missing336) ? $missing336 : 'none'), '|END';
