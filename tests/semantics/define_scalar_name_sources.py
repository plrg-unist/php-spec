#!/usr/bin/env python3
"""Native-first scalar name reception for define()."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'weak-scalar-name-publication': br'''<?php
echo 'B|';
$name = 37;
echo define(constant_name: $name, value: 137) ? 'T' : 'F';
echo '|', $name === 37 ? 'I' : 'BAD', '|', constant('37');
echo '|', define(true, 101) ? 'T' : 'F', '|', constant('1');
echo '|', define(2.5, 125, false) ? 'T' : 'F', '|', constant('2.5');
echo '|', define(false, 140) ? 'T' : 'F', '|', constant('');
ini_set('precision', '1');
echo '|', constant('2.5');
''',
    'captured-name-value-and-duplicate-warning': br'''<?php
function scalarDefineName28() {
    global $call;
    $call = 'defined';
    echo 'N|';
    return 38;
}
function scalarDefineValue28() {
    global $call;
    $call = 'constant';
    echo 'V|';
    return 138;
}
function duplicateScalar28($level, $message) {
    global $name, $candidate;
    echo '|H|', $message;
    $name = 39;
    $candidate = 777;
    return true;
}
$call = 'define';
echo 'B|';
$result = $call(constant_name: scalarDefineName28(), value: scalarDefineValue28());
echo $result ? 'T' : 'F', '|', $call, '|', constant('38');
$name = 38;
$candidate = 999;
set_error_handler('duplicateScalar28');
$result = define($name, $candidate, false);
restore_error_handler();
echo '|', $result ? 'T' : 'F', '|', constant('38');
echo '|', defined('39') ? 'T' : 'F', '|', $name, '|', $candidate;
''',
    'strict-name-errors-after-all-argument-effects': br'''<?php
declare(strict_types=1);
function strictDefineName28() { echo 'N|'; return 37; }
function strictDefineValue28() { echo 'V|'; return 137; }
echo 'B|';
$result = 99;
try {
    $result = define(constant_name: strictDefineName28(), value: strictDefineValue28());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === 37 ? 'I' : 'BAD';
    echo '|', $trace[0]['args'][1] === 137 ? 'V' : 'BAD';
}
try {
    $result = define(true, 101);
    echo '|BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][0] === true ? 'T' : 'BAD';
}
try {
    $result = define(2.5, 125, false);
    echo '|BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['args'][0] === 2.5 ? 'D' : 'BAD';
}
echo '|', $result, '|', defined('37') ? 'T' : 'F';
echo '|', defined('1') ? 'T' : 'F', '|', defined('2.5') ? 'T' : 'F';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
