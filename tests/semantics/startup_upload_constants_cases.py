"""Fixed upload-error startup integers, without upload-service execution."""

VALUES = {'UPLOAD_ERR_OK': 'PINT 0', 'UPLOAD_ERR_INI_SIZE': 'PINT 1',
          'UPLOAD_ERR_FORM_SIZE': 'PINT 2', 'UPLOAD_ERR_PARTIAL': 'PINT 3',
          'UPLOAD_ERR_NO_FILE': 'PINT 4', 'UPLOAD_ERR_NO_TMP_DIR': 'PINT 6',
          'UPLOAD_ERR_CANT_WRITE': 'PINT 7', 'UPLOAD_ERR_EXTENSION': 'PINT 8'}
ALIASES = {'NoFile': 'UPLOAD_ERR_NO_FILE'}
UNDEFINED = ('upload_ERR_OK',)

CASES = {
    'values': b'''<?php
echo UPLOAD_ERR_OK === 0, ':', UPLOAD_ERR_INI_SIZE === 1, ':',
    UPLOAD_ERR_FORM_SIZE === 2, ':', UPLOAD_ERR_PARTIAL === 3, ':',
    UPLOAD_ERR_NO_FILE === 4, ':', UPLOAD_ERR_NO_TMP_DIR === 6, ':',
    UPLOAD_ERR_CANT_WRITE === 7, ':', UPLOAD_ERR_EXTENSION === 8, ':',
    UPLOAD_ERR_OK !== false, ':', UPLOAD_ERR_EXTENSION !== 8.0;
''',
    'names': b'''<?php
namespace Startup\\Shadow {
    use const UPLOAD_ERR_NO_FILE as NoFile;
    const UPLOAD_ERR_OK = 'local';
    echo UPLOAD_ERR_OK === 'local', '|', \\UPLOAD_ERR_OK === 0, '|', NoFile === 4, '|';
}
namespace Startup\\Fallback {
    echo UPLOAD_ERR_INI_SIZE === 1, '|', UPLOAD_ERR_PARTIAL === 3, '|';
    try { echo upload_ERR_OK; } catch (\\Error $error) { echo 'case|'; }
    try { echo namespace\\UPLOAD_ERR_NO_TMP_DIR; } catch (\\Error $error) { echo 'qualified|'; }
    echo defined('UPLOAD_ERR_EXTENSION'), '|', defined('UPLOAD_ERR_5'), '|',
        constant('UPLOAD_ERR_CANT_WRITE') === 7;
}
''',
    'boundaries': b'''<?php
echo (UPLOAD_ERR_NO_TMP_DIR - UPLOAD_ERR_NO_FILE) === 2, ':',
    (UPLOAD_ERR_EXTENSION + UPLOAD_ERR_INI_SIZE) === 9, ':',
    UPLOAD_ERR_PARTIAL < UPLOAD_ERR_NO_FILE, ':', UPLOAD_ERR_OK !== false, ':',
    defined('UPLOAD_ERR_5') === false;
''',
    'defaults': b'''<?php
function upload_codes(int $ok = UPLOAD_ERR_OK, int $missing = UPLOAD_ERR_NO_TMP_DIR) {
    echo $ok === 0, ':', $missing === 6;
}
upload_codes();
''',
}

OUTPUTS = {
    'values': b'1:1:1:1:1:1:1:1:1:1',
    'names': b'1|1|1|1|1|case|qualified|1||1',
    'boundaries': b'1:1:1:1:1',
    'defaults': b'1:1',
}
