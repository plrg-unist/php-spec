#!/usr/bin/env python3
"""Independent model-only build-Boolean resolution and API controls."""
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_review as runner

CASES = {
    'qualified-errors': (b'''<?php
namespace Startup\\IndependentBuild {
    use const Missing\\PHP_ZTS as MissingThreaded;
    try { echo MissingThreaded; } catch (\\Error $error) { echo 'I'; }
    try { echo namespace\\PHP_DEBUG; } catch (\\Error $error) { echo 'R'; }
    try { echo \\php_DEBUG; } catch (\\Error $error) { echo 'C'; }
}
''', b'IRC'),
    'bool-shadow': (b'''<?php
namespace Startup\\IndependentBuildShadow {
    use const PHP_DEBUG as Debug;
    const PHP_ZTS = 1;
    echo PHP_ZTS === 1, ':', \\PHP_ZTS === false, ':',
        PHP_DEBUG === \\PHP_DEBUG, ':', Debug === false;
}
''', b'1:1:1:1'),
    'runtime-queries': (b'''<?php
namespace Startup\\IndependentBuildRuntime {
    const PHP_DEBUG = true;
    echo defined('PHP_ZTS'), defined('PHP_DEBUG'), ':',
        defined('php_debug') === false, ':', constant('PHP_ZTS') === false, ':',
        constant('PHP_DEBUG') === false, ':',
        constant('Startup\\IndependentBuildRuntime\\PHP_DEBUG') === true, ':',
        PHP_DEBUG === true;
}
''', b'11:1:1:1:1:1'),
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
                       'An integer local shadow differs from genuine false global/imported/fallback values. '
                       'Runtime global queries retain Boolean false despite a true local shadow; '
                       'an explicit qualified string resolves that local true value. '
                       'These model-only controls have no native execution or source-agreement credit.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
