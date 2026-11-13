"""Pinned binary64 startup primitives observed only through core PHP."""

CASES = {
    'values': b'''<?php
echo PHP_FLOAT_DIG === 15, ':', PHP_FLOAT_DIG !== 15.0, ':',
    PHP_FLOAT_EPSILON === 2.220446049250313e-16, ':',
    PHP_FLOAT_MAX === 1.7976931348623157e308, ':',
    PHP_FLOAT_MIN === 2.2250738585072014e-308, ':',
    PHP_FLOAT_MIN !== 5e-324;
''',
    'names': b'''<?php
namespace Startup\\Shadow {
    use const PHP_FLOAT_EPSILON as EPS;
    const PHP_FLOAT_DIG = 99;
    echo PHP_FLOAT_DIG, '|', \\PHP_FLOAT_DIG === 15, '|',
        EPS === 2.220446049250313e-16, '|';
}
namespace Startup\\Fallback {
    echo PHP_FLOAT_DIG === 15, '|',
        PHP_FLOAT_EPSILON === \\PHP_FLOAT_EPSILON, '|',
        PHP_FLOAT_MAX === \\PHP_FLOAT_MAX, '|',
        PHP_FLOAT_MIN === \\PHP_FLOAT_MIN, '|';
    try { echo php_float_DIG; } catch (\\Error $error) { echo 'case|'; }
    try { echo namespace\\PHP_FLOAT_MAX; } catch (\\Error $error) { echo 'qualified|'; }
    echo defined('PHP_FLOAT_MAX'), '|', defined('php_float_max'), '|',
        constant('PHP_FLOAT_MIN') === \\PHP_FLOAT_MIN;
}
''',
    'boundaries': b'''<?php
echo (1.0 + PHP_FLOAT_EPSILON) > 1.0, ':',
    (1.0 + PHP_FLOAT_EPSILON / 2) === 1.0, ':',
    (PHP_FLOAT_MAX * 2) === INF, ':',
    (PHP_FLOAT_MIN / 2) > 0.0, ':',
    (PHP_FLOAT_MIN / 2) < PHP_FLOAT_MIN, ':',
    PHP_FLOAT_MIN > 5e-324;
''',
    'defaults': b'''<?php
function limits(int $digits = PHP_FLOAT_DIG, float $epsilon = PHP_FLOAT_EPSILON,
    float $maximum = PHP_FLOAT_MAX, float $minimum = PHP_FLOAT_MIN) {
    echo $digits === 15, ':', $epsilon === 2.220446049250313e-16, ':',
        $maximum === 1.7976931348623157e308, ':',
        $minimum === 2.2250738585072014e-308;
}
limits();
''',
}

OUTPUTS = {
    'values': b'1:1:1:1:1:1',
    'names': b'99|1|1|1|1|1|1|case|qualified|1||1',
    'boundaries': b'1:1:1:1:1:1',
    'defaults': b'1:1:1:1',
}
