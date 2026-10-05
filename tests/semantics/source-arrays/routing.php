<?php
$round = 0;
function arrayRoutingNotice($level, $message, $file, $line) {
    global $round;
    ++$round;
    echo 'H:', $round, ':', $message, '|';
    $GLOBALS['operand'] = 'echo "wrong";';
    chdir(__DIR__ . '/late');
    set_include_path('.');
    ini_set('display_errors', 'stdout');
    return false;
}
set_error_handler('arrayRoutingNotice', E_WARNING);
set_include_path(__DIR__ . '/early');
$operand = [1];
echo 'A:', include $operand, '|';
$operand = [2];
echo 'B:', include_once $operand, '|';
echo 'C:', require_once [], '|END';
