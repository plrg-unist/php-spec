#!/usr/bin/env python3
"""Independent model-only release-string resolution and runtime API controls."""
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_review as runner

CASES = {
    'qualified-errors': (b'''<?php
namespace Startup\\IndependentRelease {
    use const Missing\\PHP_EXTRA_VERSION as MissingExtra;
    try { echo MissingExtra; } catch (\\Error $error) { echo 'I'; }
    try { echo namespace\\PHP_VERSION; } catch (\\Error $error) { echo 'R'; }
    try { echo \\Php_VERSION; } catch (\\Error $error) { echo 'C'; }
}
''', b'IRC'),
    'scalar-shadows': (b'''<?php
namespace Startup\\IndependentReleaseShadow {
    use const PHP_VERSION as Release;
    use const PHP_EXTRA_VERSION as Extra;
    const PHP_VERSION = false;
    const PHP_EXTRA_VERSION = 0;
    echo PHP_VERSION === false, ':', PHP_EXTRA_VERSION === 0, ':',
        \\PHP_VERSION === '8.5.10', ':', \\PHP_EXTRA_VERSION === '', ':',
        Release === '8.5.10', ':', Extra === '', '|', Release, '|', Extra;
}
''', b'1:1:1:1:1:1|8.5.10|'),
    'runtime-queries': (b'''<?php
namespace Startup\\IndependentReleaseRuntime {
    const PHP_VERSION = 85;
    const PHP_EXTRA_VERSION = false;
    echo defined('PHP_VERSION'), defined('PHP_EXTRA_VERSION'), ':',
        defined('php_version') === false, ':', constant('PHP_VERSION') === '8.5.10', ':',
        constant('PHP_EXTRA_VERSION') === '', ':',
        constant('Startup\\IndependentReleaseRuntime\\PHP_VERSION') === 85, ':',
        constant('Startup\\IndependentReleaseRuntime\\PHP_EXTRA_VERSION') === false, ':',
        PHP_VERSION === 85, ':', PHP_EXTRA_VERSION === false;
}
''', b'11:1:1:1:1:1:1:1'),
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
                       'Boolean and integer local shadows remain distinct from global/imported strings. '
                       'Runtime global queries retain exact case and bytes while qualified strings '
                       'resolve the local scalar values. These model-only controls add no native '
                       'execution or source agreement.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
