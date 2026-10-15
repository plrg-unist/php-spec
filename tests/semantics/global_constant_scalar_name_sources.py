#!/usr/bin/env python3
"""Native-first scalar name reception for constant() and defined()."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'weak-scalar-name-lookups': br'''<?php
define('37', 137);
define('1', 101);
define('2.5', 125);
echo 'B|';
echo constant(name: 37), '|', constant(true), '|', constant(2.5);
echo '|', defined(37) ? 'T' : 'F', '|', defined(constant_name: true) ? 'T' : 'F';
echo '|', defined(2.5) ? 'T' : 'F', '|', defined(false) ? 'T' : 'F';
''',
    'captured-scalar-query-and-converted-error-arg': br'''<?php
define('37', 137);
function scalarQueryName27() {
    global $call;
    $call = 'defined';
    echo 'Q|';
    return 37;
}
$call = 'constant';
echo 'B|';
$value = $call(name: scalarQueryName27());
echo $value, '|', $call;
$result = 99;
try {
    $result = constant(name: 404);
    echo '|BAD';
} catch (Error $e) {
    $trace = $e->getTrace();
    echo '|', $result, '|', $e->getMessage(), '|', $e->getLine();
    echo '|', $trace[0]['function'], '|', $trace[0]['args'][0];
    echo '|', $trace[0]['args'][0] === '404' ? 'S' : ($trace[0]['args'][0] === 404 ? 'I' : 'O');
}
''',
    'strict-scalar-name-type-errors': br'''<?php
declare(strict_types=1);
echo 'B|';
$result = 99;
try {
    $result = constant(name: 37);
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === 37 ? 'I' : 'O';
}
try {
    $result = defined(constant_name: true);
    echo '|BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === true ? 'T' : 'O';
}
try {
    $result = constant(2.5);
    echo '|BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === 2.5 ? 'D' : 'O';
}
echo '|', $result;
''',
}
family.BASELINE = ('class constant value query', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
