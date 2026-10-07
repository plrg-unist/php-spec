<?php
class AutoGlobalPayload316 { public $value = 'initial'; }
class AutoGlobalOperand316 {
    public function __toString(): string { echo 'cast|'; $_GET->value = 'cast'; return __DIR__ . '/autoglobal-property-child.php'; }
    public function __destruct() {
        source_auto_global_ready_316();
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'READY:', $_GET->value, '|';
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/autoglobal-property-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/autoglobal-property-child.php' ? 'filename' : 'none'), '|';
        throw $error;
    }
}
$_GET = new AutoGlobalPayload316;
$value = 'before';
try {
    $value = include new AutoGlobalOperand316;
    echo 'AFTER-BODY|';
} catch (Throwable $error) { echo 'caught|'; }
echo 'G:', $_GET->value, '|V:', $value, '|END';
