<?php
function sourceEmptyNotice($level, $message, $file, $line) {
    echo 'H:', $level, ':', $message, ':', $line, '|';
    $GLOBALS['cvMissing'] = 'replacement.php';
    set_include_path('callback-path');
    return true;
}
set_error_handler('sourceEmptyNotice', E_WARNING);
try { echo 'I:', include $cvMissing, '|'; } catch (Throwable $e) { echo 'EI:', $e->getMessage(), '|', $e->getTraceAsString(), '|'; }
unset($cvMissing);
try { echo 'O:', include_once $cvMissing, '|'; } catch (Throwable $e) { echo 'EO:', $e->getMessage(), '|'; }
unset($cvMissing);
try { echo 'R:', require $cvMissing, '|'; } catch (Throwable $e) { echo 'ER:', $e->getMessage(), '|'; }
unset($cvMissing);
try { echo 'Q:', require_once $cvMissing, '|'; } catch (Throwable $e) { echo 'EQ:', $e->getMessage(), '|'; }
restore_error_handler();
echo 'V:', $cvMissing, ':', get_include_path(), '|END';
