#!/usr/bin/env python3
"""Independent model-only upload-code resolution and API controls."""
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_review as runner

CASES = {
    'qualified-errors': (b'''<?php
namespace Startup\\IndependentUpload {
    use const Missing\\UPLOAD_ERR_INI_SIZE as MissingStatus;
    try { echo MissingStatus; } catch (\\Error $error) { echo 'I'; }
    try { echo namespace\\UPLOAD_ERR_EXTENSION; } catch (\\Error $error) { echo 'R'; }
    try { echo \\upload_ERR_OK; } catch (\\Error $error) { echo 'C'; }
}
''', b'IRC'),
    'zero-shadow': (b'''<?php
namespace Startup\\IndependentUploadShadow {
    use const UPLOAD_ERR_NO_TMP_DIR as NoTemp;
    const UPLOAD_ERR_OK = false;
    echo UPLOAD_ERR_OK === false, ':', \\UPLOAD_ERR_OK === 0, ':',
        UPLOAD_ERR_PARTIAL === 3, ':', NoTemp === 6;
}
''', b'1:1:1:1'),
    'runtime-queries': (b'''<?php
namespace Startup\\IndependentUploadRuntime {
    const UPLOAD_ERR_NO_FILE = false;
    echo defined('UPLOAD_ERR_OK'), defined('UPLOAD_ERR_INI_SIZE'),
        defined('UPLOAD_ERR_FORM_SIZE'), defined('UPLOAD_ERR_PARTIAL'),
        defined('UPLOAD_ERR_NO_FILE'), defined('UPLOAD_ERR_NO_TMP_DIR'),
        defined('UPLOAD_ERR_CANT_WRITE'), defined('UPLOAD_ERR_EXTENSION'), ':',
        defined('UPLOAD_ERR_5') === false, ':', defined('upload_err_ok') === false, ':',
        constant('UPLOAD_ERR_OK') === 0, ':', constant('UPLOAD_ERR_NO_FILE') === 4, ':',
        constant('UPLOAD_ERR_NO_TMP_DIR') === 6, ':', constant('UPLOAD_ERR_EXTENSION') === 8, ':',
        constant('Startup\\IndependentUploadRuntime\\UPLOAD_ERR_NO_FILE') === false, ':',
        UPLOAD_ERR_NO_FILE === false;
}
''', b'11111111:1:1:1:1:1:1:1:1'),
}

if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    runner.CASES = CASES
    passed = runner.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'][str(own.relative_to(runner.ROOT))] = before
    report['scope'] = ('Missing imports, explicit relative names and wrong final case raise caught Error. '
                       'A false local shadow stays distinct from genuine integer zero and imported/fallback codes. '
                       'Runtime queries preserve all eight registered names, the missing code-five name, exact '
                       'global integer values and an explicit qualified local false value. '
                       'These model-only controls add no native execution, source agreement or upload-service credit.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
