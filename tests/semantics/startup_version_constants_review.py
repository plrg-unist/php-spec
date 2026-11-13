#!/usr/bin/env python3
"""Independent model-only release-integer resolution and API controls."""
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_review as runner

CASES = {
    'qualified-errors': (b'''<?php
namespace Startup\\Independent {
    use const Missing\\PHP_MINOR_VERSION as MissingVersion;
    try { echo MissingVersion; } catch (\\Error $error) { echo 'I'; }
    try { echo namespace\\PHP_VERSION_ID; } catch (\\Error $error) { echo 'R'; }
    try { echo \\php_MAJOR_VERSION; } catch (\\Error $error) { echo 'C'; }
}
''', b'IRC'),
    'version-shadow': (b'''<?php
namespace Startup\\IndependentShadow {
    use const PHP_RELEASE_VERSION as Patch;
    const PHP_MINOR_VERSION = 'local';
    echo PHP_MINOR_VERSION === 'local', ':', \\PHP_MINOR_VERSION === 5, ':',
        PHP_MAJOR_VERSION === \\PHP_MAJOR_VERSION, ':', Patch === 10;
}
''', b'1:1:1:1'),
    'runtime-queries': (b'''<?php
namespace Startup\\Runtime {
    const PHP_VERSION_ID = 3;
    echo defined('PHP_MAJOR_VERSION'), defined('PHP_MINOR_VERSION'),
        defined('PHP_RELEASE_VERSION'), defined('PHP_VERSION_ID'), ':',
        defined('php_version_id') === false, ':',
        constant('PHP_MAJOR_VERSION') === 8, ':', constant('PHP_MINOR_VERSION') === 5, ':',
        constant('PHP_RELEASE_VERSION') === 10, ':', constant('PHP_VERSION_ID') === 80510, ':',
        constant('Startup\\Runtime\\PHP_VERSION_ID') === 3, ':', PHP_VERSION_ID === 3;
}
''', b'1111:1:1:1:1:1:1:1'),
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
                       'A string-typed local shadow differs from genuine global/imported/fallback integers. '
                       'Runtime string queries retain exact names and values independently of lexical namespace. '
                       'These model-only controls have no native execution or source-agreement credit.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
