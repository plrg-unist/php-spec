"""Boolean startup facts for the pinned nondebug, non-thread-safe runtime."""

VALUES = {'PHP_ZTS': 'PBOOL false', 'PHP_DEBUG': 'PBOOL false'}
ALIASES = {'Threaded': 'PHP_ZTS'}
UNDEFINED = ('php_ZTS',)

CASES = {
    'values': b'''<?php
echo PHP_ZTS === false, ':', PHP_DEBUG === false, ':',
    PHP_ZTS !== 0, ':', PHP_DEBUG !== 0, ':', PHP_ZTS !== '', ':', PHP_DEBUG !== null;
''',
    'names': b'''<?php
namespace Startup\\Shadow {
    use const PHP_ZTS as Threaded;
    const PHP_DEBUG = 'local';
    echo PHP_DEBUG === 'local', '|', \\PHP_DEBUG === false, '|', Threaded === false, '|';
}
namespace Startup\\Fallback {
    echo PHP_ZTS === false, '|', PHP_DEBUG === \\PHP_DEBUG, '|';
    try { echo php_ZTS; } catch (\\Error $error) { echo 'case|'; }
    try { echo namespace\\PHP_DEBUG; } catch (\\Error $error) { echo 'qualified|'; }
    echo defined('PHP_ZTS'), '|', defined('php_zts'), '|', constant('PHP_DEBUG') === false;
}
''',
    'boundaries': b'''<?php
echo (PHP_ZTS || PHP_DEBUG) === false, ':', (PHP_ZTS && PHP_DEBUG) === false, ':',
    (PHP_ZTS xor PHP_DEBUG) === false, ':', (!PHP_ZTS) === true, ':',
    PHP_DEBUG ? 'bad' : 'quiet';
''',
    'defaults': b'''<?php
function startup_flags(bool $threaded = PHP_ZTS, bool $debug = PHP_DEBUG) {
    echo $threaded === false, ':', $debug === false;
}
startup_flags();
''',
}

OUTPUTS = {
    'values': b'1:1:1:1:1:1',
    'names': b'1|1|1|1|1|case|qualified|1||1',
    'boundaries': b'1:1:1:1:quiet',
    'defaults': b'1:1',
}
