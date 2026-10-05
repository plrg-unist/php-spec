<?php
$round = 0;
function coreArraySourceNotice($level, $message, $file, $line) {
    global $round;
    ++$round;
    echo 'H:', $round, '|';
    if ($round === 1) {
        $GLOBALS['operand'] = 'replacement.php';
        set_include_path(__DIR__ . '/late');
        echo 'Replaced|';
    }
    return true;
}
set_error_handler('coreArraySourceNotice', E_WARNING);
set_include_path(__DIR__ . '/early');
$operand = [$round];
echo 'B:', include $operand, '|';
set_include_path(__DIR__ . '/early');
echo 'T:', include [$round], '|';
set_include_path(__DIR__ . '/late');
echo 'O:', include_once [], '|END';
