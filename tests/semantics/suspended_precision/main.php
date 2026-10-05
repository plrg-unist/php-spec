<?php
$turn = 0;
function precisionChronologyNotice($level, $message, $file, $line) {
    global $turn;
    $turn++;
    echo 'H', $turn, ':', ini_get('precision'), ':', PrecisionBefore::MARK, ':';
    try { echo PrecisionBetween::MARK; } catch (Error $error) { echo '-'; }
    if ($turn === 2) {
        echo ':';
        try { echo PrecisionAfter::MARK; } catch (Error $error) { echo '-'; }
    }
    echo '|';
    ini_set('precision', $turn === 1 ? '1tail' : '2tail');
    $suffix = 'H';
    echo 'C:', 12.3456789 . $suffix, '|';
    return true;
}
set_error_handler('precisionChronologyNotice');
ini_set('precision', '3tail');
eval(<<<'PHP'
$suffix = 'X';
class PrecisionBefore { const MARK = 'A'; }
$before = 12.3456789 . $suffix;
function precisionWarningA($x) { return "${x}"; }
class PrecisionBetween { const MARK = 'B'; }
$between = 12.3456789 . $suffix;
function precisionWarningB($x) { return "${x}"; }
class PrecisionAfter { const MARK = 'C'; }
$after = 12.3456789 . $suffix;
$parser = 12.3456789 . 'L';
echo 'B:', $before, '|M:', $between, '|A:', $after, '|P:', $parser, '|';
PHP);
echo 'R:', ini_get('precision'), '|END';
