<?php
class DeferredRegularSource {
    public function __toString(): string {
        echo 'T|';
        return "echo\n    'eval-body';\nreturn 52;\n";
    }
    public function __destruct() {
        echo "D:registered|";
        $error = new Exception('deferred');
        foreach ($error->getTrace() as $frame) {
            echo 'F:', $frame['function'], ':', $frame['line'], ':', ($frame['file'] === __FILE__ ? 'main' : 'eval'), ':';
            if (isset($frame['args'][0])) { echo 'ARG:', ($frame['args'][0] === $this ? 'object' : 'code'); }
            else { echo 'NOARG'; }
            echo '|';
        }
        throw $error;
    }
}
$value = 'old';
try {
    $value = eval(new DeferredRegularSource);
    echo 'A:', $value, '|';
    error_reporting(1);
    echo 'skipped|';
} catch (Throwable $error) {
    foreach ($error->getTrace() as $frame) { echo 'F:', $frame['function'], ':', $frame['line'], '|'; }
}
echo 'V:', $value, '|R:', error_reporting(), '|END';
