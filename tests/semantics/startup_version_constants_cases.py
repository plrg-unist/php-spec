"""Fixed release integers from the vendored PHP 8.5.10 version header."""

VALUES = {'PHP_MAJOR_VERSION': 'PINT 8', 'PHP_MINOR_VERSION': 'PINT 5',
          'PHP_RELEASE_VERSION': 'PINT 10', 'PHP_VERSION_ID': 'PINT 80510'}
ALIASES = {'Major': 'PHP_MAJOR_VERSION'}
UNDEFINED = ('php_VERSION_ID',)

CASES = {
    'values': b'''<?php
echo PHP_MAJOR_VERSION === 8, ':', PHP_MINOR_VERSION === 5, ':',
    PHP_RELEASE_VERSION === 10, ':', PHP_VERSION_ID === 80510, ':',
    PHP_MAJOR_VERSION !== 8.0, ':', PHP_VERSION_ID !== 80510.0;
''',
    'names': b'''<?php
namespace Startup\\Shadow {
    use const PHP_MAJOR_VERSION as Major;
    const PHP_VERSION_ID = 7;
    echo PHP_VERSION_ID, '|', \\PHP_VERSION_ID === 80510, '|', Major === 8, '|';
}
namespace Startup\\Fallback {
    echo PHP_MAJOR_VERSION === 8, '|', PHP_MINOR_VERSION === 5, '|',
        PHP_RELEASE_VERSION === 10, '|', PHP_VERSION_ID === \\PHP_VERSION_ID, '|';
    try { echo php_VERSION_ID; } catch (\\Error $error) { echo 'case|'; }
    try { echo namespace\\PHP_MAJOR_VERSION; } catch (\\Error $error) { echo 'qualified|'; }
    echo defined('PHP_VERSION_ID'), '|', defined('php_version_id'), '|',
        constant('PHP_RELEASE_VERSION') === 10;
}
''',
    'boundaries': b'''<?php
echo (PHP_MAJOR_VERSION * 10000 + PHP_MINOR_VERSION * 100 + PHP_RELEASE_VERSION) === PHP_VERSION_ID, ':',
    PHP_VERSION_ID >= 80500, ':', PHP_VERSION_ID < 80600, ':',
    (PHP_VERSION_ID % 100) === PHP_RELEASE_VERSION, ':',
    (PHP_MINOR_VERSION + PHP_RELEASE_VERSION) === 15;
''',
    'defaults': b'''<?php
function release_parts(int $major = PHP_MAJOR_VERSION, int $minor = PHP_MINOR_VERSION,
    int $release = PHP_RELEASE_VERSION, int $id = PHP_VERSION_ID) {
    echo $major === 8, ':', $minor === 5, ':', $release === 10, ':', $id === 80510;
}
release_parts();
''',
}

OUTPUTS = {
    'values': b'1:1:1:1:1:1',
    'names': b'7|1|1|1|1|1|1|case|qualified|1||1',
    'boundaries': b'1:1:1:1:1',
    'defaults': b'1:1:1:1',
}
