<?php
function sourceEvalThrow($level, $message, $file, $line) {
    echo 'H:', $message, ':', $line, '|';
    $GLOBALS['cvThrow'] = 'echo "wrong-body|";';
    $trace = new Exception('mark');
    echo $trace->getTraceAsString(), '|';
    throw new Exception('stop');
}
set_error_handler('sourceEvalThrow', E_WARNING);
try { eval($cvThrow); echo 'wrong-after|'; }
catch (Exception $e) { echo 'E:', $e->getMessage(), ':', $cvThrow, '|'; }
restore_error_handler();
echo 'END';
