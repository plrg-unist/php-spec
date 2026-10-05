<?php
function precisionDeferredNotice($level, $message, $file, $line) {
    echo 'H:', ini_get('precision'), '|';
    ini_set('precision', '1tail');
    return true;
}
set_error_handler('precisionDeferredNotice');
class PrecisionDeferred {
    const VALUE = E_STRICT . 12.3456789;
}
echo 'V:', PrecisionDeferred::VALUE, '|END';
