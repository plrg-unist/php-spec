#!/usr/bin/env python3
"""Native-first null name reception and deprecation before constant lookup."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'callback-publication-before-empty-name-lookup': br'''<?php
function publishNullName29($level, $message) {
    global $name, $call;
    echo 'H|', $level, '|', $message, '|';
    if (!defined('')) { define('', 129); }
    $name = 'changed';
    $call = 'defined';
    return true;
}
$name = null;
$call = 'constant';
set_error_handler('publishNullName29');
echo 'B|';
$result = $call(name: $name);
echo $result, '|', $name, '|', $call, '|';
echo defined(constant_name: null) ? 'T' : 'F';
restore_error_handler();
''',
    'default-deprecation-and-converted-missing-error': br'''<?php
function reportNullName29($level, $message) {
    echo 'H|', $level, '|', $message, '|';
    return false;
}
set_error_handler('reportNullName29');
echo 'B|';
echo defined(null) ? 'T' : 'F';
$name = null;
$result = 99;
try {
    $result = constant(name: $name);
    echo '|BAD';
} catch (Error $e) {
    $trace = $e->getTrace();
    echo '|', $name === null ? 'N' : 'BAD', '|', $result;
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === '' ? 'S' : 'BAD';
} finally {
    restore_error_handler();
    echo '|Z';
}
''',
    'strict-null-name-errors-without-deprecation': br'''<?php
declare(strict_types=1);
function rejectNullHandler29($level, $message) { echo 'BAD-H|'; return true; }
function strictNullName29() { echo 'N|'; return null; }
set_error_handler('rejectNullHandler29');
echo 'B|';
$result = 99;
try {
    $result = constant(name: strictNullName29());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
}
try {
    $result = defined(constant_name: null);
    echo '|BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
}
restore_error_handler();
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
