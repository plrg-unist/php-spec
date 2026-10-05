<?php
class ArrayOperandPayload {
    public $tag;
    public function __construct($tag) { $this->tag = $tag; }
    public function __destruct() {
        echo 'D:', $this->tag, '|';
        set_include_path(__DIR__ . '/late');
    }
}
$round = 0;
function arrayOperandNotice($level, $message, $file, $line) {
    global $round;
    ++$round;
    echo 'H:', $round, '|';
    if ($round === 1) {
        $GLOBALS['borrowed'] = [];
        echo 'Replaced|';
    }
    return true;
}
set_error_handler('arrayOperandNotice', E_WARNING);
set_include_path(__DIR__ . '/early');
$borrowed = [new ArrayOperandPayload('borrowed')];
echo 'B:', include $borrowed, '|';
set_include_path(__DIR__ . '/early');
echo 'T:', include [new ArrayOperandPayload('temporary')], '|';
set_include_path(__DIR__ . '/late');
echo 'O:', include_once [], '|END';
