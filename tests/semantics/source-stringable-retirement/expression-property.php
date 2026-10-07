<?php
class EmissionPayload314 { public $value = 'payload'; }
function emission_object_314() { echo 'CALL-BODY|'; return $GLOBALS['emission_object_314']; }
class EmissionOperand314 {
    public function __toString(): string { return __DIR__ . '/property-child.php'; }
    public function __destruct() {
        source_emission_ready_314();
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/property-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/property-child.php' ? 'filename' : 'none'), '|';
        throw $error;
    }
}
$emission_value_314 = 'payload';
$emission_object_314 = new EmissionPayload314;
$value = 'before';
try {
    $value = include new EmissionOperand314;
    echo 'AFTER-BODY|';
} catch (Throwable $error) { echo 'caught|'; }
echo 'V:', $value, '|END';
