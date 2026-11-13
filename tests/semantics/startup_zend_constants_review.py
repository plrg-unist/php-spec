#!/usr/bin/env python3
"""Independent model-only Zend scalar resolution and runtime API controls."""
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_review as runner

CASES = {
    'qualified-errors': (b'''<?php
namespace Startup\\IndependentZend {
    use const Missing\\DEBUG_BACKTRACE_PROVIDE_OBJECT as MissingFlag;
    try { echo MissingFlag; } catch (\\Error $error) { echo 'I'; }
    try { echo namespace\\ZEND_THREAD_SAFE; } catch (\\Error $error) { echo 'R'; }
    try { echo \\zend_DEBUG_BUILD; } catch (\\Error $error) { echo 'C'; }
}
''', b'IRC'),
    'scalar-shadows': (b'''<?php
namespace Startup\\IndependentZendShadow {
    use const DEBUG_BACKTRACE_PROVIDE_OBJECT as ObjectFlag;
    const ZEND_THREAD_SAFE = 0;
    const DEBUG_BACKTRACE_IGNORE_ARGS = true;
    echo ZEND_THREAD_SAFE === 0, ':', \\ZEND_THREAD_SAFE === false, ':',
        DEBUG_BACKTRACE_IGNORE_ARGS === true, ':', \\DEBUG_BACKTRACE_IGNORE_ARGS === 2, ':',
        ObjectFlag === 1, ':', ZEND_DEBUG_BUILD === false;
}
''', b'1:1:1:1:1:1'),
    'runtime-queries': (b'''<?php
namespace Startup\\IndependentZendRuntime {
    const ZEND_DEBUG_BUILD = 1;
    const DEBUG_BACKTRACE_PROVIDE_OBJECT = false;
    echo defined('ZEND_THREAD_SAFE'), defined('ZEND_DEBUG_BUILD'),
        defined('DEBUG_BACKTRACE_PROVIDE_OBJECT'), defined('DEBUG_BACKTRACE_IGNORE_ARGS'), ':',
        defined('zend_debug_build') === false, ':', constant('ZEND_THREAD_SAFE') === false, ':',
        constant('ZEND_DEBUG_BUILD') === false, ':',
        constant('DEBUG_BACKTRACE_PROVIDE_OBJECT') === 1, ':',
        constant('DEBUG_BACKTRACE_IGNORE_ARGS') === 2, ':',
        constant('Startup\\IndependentZendRuntime\\ZEND_DEBUG_BUILD') === 1, ':',
        constant('Startup\\IndependentZendRuntime\\DEBUG_BACKTRACE_PROVIDE_OBJECT') === false, ':',
        ZEND_DEBUG_BUILD === 1, ':', DEBUG_BACKTRACE_PROVIDE_OBJECT === false;
}
''', b'1111:1:1:1:1:1:1:1:1:1'),
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
                       'Integer and Boolean local shadows differ from the genuine global, imported '
                       'and fallback scalars. Runtime queries retain all four exact global names '
                       'and primitive types while qualified strings resolve the local shadows. '
                       'These model-only controls add no native execution, source agreement or trace/debug API credit.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
