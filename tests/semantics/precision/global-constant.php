<?php
function precisionGlobalNotice($level, $message, $file, $line) {
    echo 'H:', ini_get('precision'), '|';
    ini_set('precision', '1tail');
    $suffix = 'X';
    echo 'C:', 12.3456789 . $suffix, '|';
    return true;
}
set_error_handler('precisionGlobalNotice');
const PRECISION_GLOBAL = E_STRICT . 12.3456789;
echo 'G:', PRECISION_GLOBAL, '|END';
