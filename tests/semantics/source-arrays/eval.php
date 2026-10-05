<?php
class ArrayEvalPayload { public $value = 7; }
$round = 0;
function arrayEvalNotice($level, $message, $file, $line) {
    global $round;
    ++$round;
    echo 'H:', $round, ':', $message, ':', $line, '|';
    $GLOBALS['operand'] = 'echo "wrong";';
    return true;
}
set_error_handler('arrayEvalNotice', E_WARNING);
$operand = [1];
try { eval($operand); } catch (ParseError $e) { echo 'P:', $e->getMessage(), '|'; }
try { eval([new ArrayEvalPayload]); } catch (ParseError $e) { echo 'T:', $e->getMessage(), '|'; }
restore_error_handler();
echo 'V:', $operand, '|END';
