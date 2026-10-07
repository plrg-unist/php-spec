<?php
class SourceCvText {
    public function __toString() {
        ++$GLOBALS['converted'];
        echo 'wrong-conversion|';
        return 'echo "wrong-body|";';
    }
}
$round = 0;
$converted = 0;
function sourceCvNotice($level, $message, $file, $line) {
    global $round;
    ++$round;
    echo 'H:', $round, ':', $message, ':', $line, '|';
    if ($round === 1) { $GLOBALS['cvCode'] = 'echo "wrong-body|";'; }
    if ($round === 2) { $GLOBALS['cvObject'] = new SourceCvText; }
    if ($round === 3) { $GLOBALS['cvArray'] = [7]; }
    if ($round === 4) { unset($GLOBALS['cvAbsent']); }
    ini_set('error_reporting', '0');
    return false;
}
set_error_handler('sourceCvNotice', E_WARNING);
echo 'A:', eval($cvCode) === false ? 'false' : 'other', '|';
echo 'B:', eval($cvObject) === false ? 'false' : 'other', '|';
echo 'C:', eval($cvArray) === false ? 'false' : 'other', '|';
echo 'D:', eval($cvAbsent) === false ? 'false' : 'other', '|';
restore_error_handler();
echo 'N:', $round, ':', $converted, '|END';
