"""Fixed Zend startup scalars, without trace or debug API execution."""

VALUES = {'ZEND_THREAD_SAFE': 'PBOOL false', 'ZEND_DEBUG_BUILD': 'PBOOL false',
          'DEBUG_BACKTRACE_PROVIDE_OBJECT': 'PINT 1', 'DEBUG_BACKTRACE_IGNORE_ARGS': 'PINT 2'}
ALIASES = {'TraceObject': 'DEBUG_BACKTRACE_PROVIDE_OBJECT'}
UNDEFINED = ('zend_DEBUG_BUILD',)

CASES = {
    'values': b'''<?php
echo ZEND_THREAD_SAFE === false, ':', ZEND_DEBUG_BUILD === false, ':',
    DEBUG_BACKTRACE_PROVIDE_OBJECT === 1, ':', DEBUG_BACKTRACE_IGNORE_ARGS === 2, ':',
    ZEND_THREAD_SAFE !== 0, ':', ZEND_DEBUG_BUILD !== 0, ':',
    DEBUG_BACKTRACE_PROVIDE_OBJECT !== true, ':', DEBUG_BACKTRACE_IGNORE_ARGS !== 2.0;
''',
    'names': b'''<?php
namespace Startup\\Shadow {
    use const DEBUG_BACKTRACE_PROVIDE_OBJECT as TraceObject;
    const ZEND_THREAD_SAFE = 0;
    echo ZEND_THREAD_SAFE === 0, '|', \\ZEND_THREAD_SAFE === false, '|', TraceObject === 1, '|';
}
namespace Startup\\Fallback {
    echo ZEND_DEBUG_BUILD === false, '|', DEBUG_BACKTRACE_IGNORE_ARGS === 2, '|';
    try { echo zend_DEBUG_BUILD; } catch (\\Error $error) { echo 'case|'; }
    try { echo namespace\\ZEND_THREAD_SAFE; } catch (\\Error $error) { echo 'qualified|'; }
    echo defined('ZEND_THREAD_SAFE'), '|', defined('zend_thread_safe'), '|',
        constant('ZEND_DEBUG_BUILD') === false;
}
''',
    'boundaries': b'''<?php
echo (DEBUG_BACKTRACE_PROVIDE_OBJECT | DEBUG_BACKTRACE_IGNORE_ARGS) === 3, ':',
    (DEBUG_BACKTRACE_PROVIDE_OBJECT & DEBUG_BACKTRACE_IGNORE_ARGS) === 0, ':',
    ZEND_THREAD_SAFE === PHP_ZTS, ':', ZEND_DEBUG_BUILD === PHP_DEBUG;
''',
    'defaults': b'''<?php
function zend_facts(int $flags = DEBUG_BACKTRACE_PROVIDE_OBJECT,
    bool $threaded = ZEND_THREAD_SAFE, bool $debug = ZEND_DEBUG_BUILD) {
    echo $flags === 1, ':', $threaded === false, ':', $debug === false;
}
zend_facts();
''',
}

OUTPUTS = {
    'values': b'1:1:1:1:1:1:1:1',
    'names': b'1|1|1|1|1|case|qualified|1||1',
    'boundaries': b'1:1:1:1',
    'defaults': b'1:1:1',
}
