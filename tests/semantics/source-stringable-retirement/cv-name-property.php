<?php
class CvNameTarget330 { public $value = 'before'; }
class CvNameOperand330 {
    public function __toString(): string { global $target330, $name330; echo 'cast|'; $target330->value = 'cast'; $name330 = 'cast330'; return __DIR__ . '/cv-name-property-child.php'; }
    public function __destruct() {
        global $target330, $name330;
        source_cv_ready_330();
        $error = new Exception('retirement');
        $trace = $error->getTrace();
        echo 'READY:', $target330->value, ':', $name330, '|';
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/cv-name-property-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/cv-name-property-child.php' ? 'filename' : 'none'), '|';
        throw $error;
    }
}
function source_cv_warning_330($code, $message, $file, $line) { echo 'W:', $line, ':', $message, '|'; return true; }
set_error_handler('source_cv_warning_330');
$target330 = new CvNameTarget330; $name330 = 'unused330';
$value = 'before';
try {
    $value = include new CvNameOperand330;
    echo 'AFTER-BODY|';
} catch (Throwable $error) { echo 'caught|'; }
echo 'N:', $name330, '|T:', $target330->value, '|V:', $value, '|H:', (isset($missing330) ? $missing330 : 'none'), '|END';
