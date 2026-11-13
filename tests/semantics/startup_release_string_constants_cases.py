"""Interned release strings fixed by the pinned PHP version header."""

VALUES = {'PHP_VERSION': 'PSTRING ([56, 46, 53, 46, 49, 48])', 'PHP_EXTRA_VERSION': 'PSTRING eps'}
ALIASES = {'Release': 'PHP_VERSION', 'Extra': 'PHP_EXTRA_VERSION'}
UNDEFINED = ('php_VERSION',)
WATCHED = ('spec/semantics/30-string-carriers.watsup',
           'spec/semantics/33-runtime-compiler.watsup',
           'spec/semantics/45-constant-context.watsup',
           'spec/semantics/89-constant-classes.watsup',
           'spec/semantics/400-dynamic-constants.watsup')

CASES = {
    'values': b'''<?php
echo PHP_VERSION === '8.5.10', ':', PHP_EXTRA_VERSION === '', ':',
    PHP_VERSION !== 8.510, ':', PHP_EXTRA_VERSION !== null, ':',
    PHP_VERSION, '|', PHP_EXTRA_VERSION;
''',
    'names': b'''<?php
namespace Startup\\Shadow {
    use const PHP_VERSION as Release;
    use const PHP_EXTRA_VERSION as Extra;
    const PHP_VERSION = 'local';
    echo PHP_VERSION === 'local', '|', \\PHP_VERSION === '8.5.10', '|',
        Release === '8.5.10', '|', Extra === '', '|';
}
namespace Startup\\Fallback {
    echo PHP_VERSION === '8.5.10', '|', PHP_EXTRA_VERSION === '', '|';
    try { echo php_VERSION; } catch (\\Error $error) { echo 'case|'; }
    try { echo namespace\\PHP_VERSION; } catch (\\Error $error) { echo 'qualified|'; }
    echo defined('PHP_VERSION'), '|', defined('php_version'), '|',
        constant('PHP_EXTRA_VERSION') === '';
}
''',
    'boundaries': b'''<?php
const RELEASE_COPY = PHP_VERSION;
const EXTRA_COPY = PHP_EXTRA_VERSION;
$version = PHP_VERSION;
$extra = PHP_EXTRA_VERSION;
echo RELEASE_COPY === '8.5.10', ':', EXTRA_COPY === '', ':',
    $version === '8.5.10', ':', $extra === '', ':',
    (bool) PHP_VERSION, ':', (bool) PHP_EXTRA_VERSION, ':',
    constant('PHP_VERSION') === RELEASE_COPY;
''',
    'defaults': b'''<?php
function release_facts(string $version = PHP_VERSION, string $extra = PHP_EXTRA_VERSION) {
    echo $version === '8.5.10', ':', $extra === '', '|';
}
release_facts();
release_facts();
''',
}

OUTPUTS = {
    'values': b'1:1:1:1:8.5.10|',
    'names': b'1|1|1|1|1|1|case|qualified|1||1',
    'boundaries': b'1:1:1:1:1::1',
    'defaults': b'1:1|1:1|',
}
