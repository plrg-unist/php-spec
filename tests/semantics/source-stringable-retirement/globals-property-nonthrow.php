<?php
class GlobalsPayload320 { public $value = 'initial'; }
class GlobalsOperand320 {
    public function __toString(): string { echo 'cast|'; $GLOBALS['payload']->value = 'cast'; return __DIR__ . '/globals-property-nonthrow-child.php'; }
    public function __destruct() {
        source_globals_ready_320();
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'READY:', $GLOBALS['payload']->value, '|';
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/globals-property-nonthrow-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/globals-property-nonthrow-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|';
    }
}
$payload = new GlobalsPayload320;
$value = 'before';
try {
    $value = include new GlobalsOperand320;
    echo 'AFTER-BODY|';
} catch (Throwable $error) { echo 'caught|'; }
echo 'G:', $GLOBALS['payload']->value, '|V:', $value, '|END';
