<?php
function computed_name_write_327() { echo 'NAME|'; return 'missing327'; }
function computed_warning_write_327($code, $message, $file, $line) {
    global $missing327;
    echo 'W:', $line, ':', $message, '|';
    $missing327 = 'handler';
    return true;
}
set_error_handler('computed_warning_write_327');
$value327 =
    ${
        computed_name_write_327()
    };
echo ($value327 === null ? 'NULL|' : 'OTHER|'), $missing327, '|END';
