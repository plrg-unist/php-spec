#!/usr/bin/env python3
"""Native-first duplicate definitions preserve modeled startup primitives."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-startup-duplicates-keep-original-values': br'''<?php
echo 'B|';
echo define('PHP_INT_SIZE', 801) ? 'BAD' : 'F', '|', constant('PHP_INT_SIZE');
echo '|', define('E_WARNING', 802, false) ? 'BAD' : 'F', '|', constant('E_WARNING');
echo '|', define('INF', 803, false) ? 'BAD' : 'F', '|', constant('INF') === INF ? 'I' : 'BAD';
''',
    'captured-startup-name-before-returning-duplicate-effects': br'''<?php
function startupValue43() {
    global $name, $candidate, $call;
    echo 'V|'; $name = 'value-name'; $candidate = 997; $call = 'constant';
    $part = 'outer'; return $part . '-value43';
}
function reportStartup43($level, $message) {
    global $name, $candidate, $call, $count;
    echo 'H|', $level, '|', $message, '|'; $count++;
    define('StartupSibling43', 819);
    $name = 'handler-name'; $candidate = 777; $call = 'defined';
    return false;
}
function startupCaller43() {
    global $name, $candidate, $call, $count;
    $part = 'PHP_INT'; $name = $part . '_SIZE'; $candidate = 0;
    $call = 'define'; $count = 0; $result = 99;
    set_error_handler('reportStartup43');
    try {
        $result = $call(constant_name: $name, value: startupValue43(), case_insensitive: false);
        echo $result === false ? 'F' : 'BAD', '|', constant('PHP_INT_SIZE');
        echo '|', constant('StartupSibling43'), '|', $name, '|', $candidate, '|', $call, '|', $count;
        echo '|', defined('handler-name') ? 'BAD' : 'F';
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; startupCaller43();
''',
    'strict-startup-duplicate-after-all-argument-effects': br'''<?php
declare(strict_types=1);
function strictStartupValue43() { global $call; echo 'V|'; $call = 'constant'; return 831; }
function strictStartupName43() { global $call; echo 'N|'; $call = 'defined'; $part = 'PHP_INT'; return $part . '_SIZE'; }
function strictStartupHandler43($level, $message) { global $count; echo 'H|', $level, '|', $message, '|'; $count++; return true; }
$call = 'define'; $result = 99; $count = 0;
set_error_handler('strictStartupHandler43');
echo 'B|';
$result = $call(value: strictStartupValue43(), constant_name: strictStartupName43(), case_insensitive: false);
restore_error_handler();
echo $result === false ? 'F' : 'BAD', '|', constant('PHP_INT_SIZE'), '|', $call, '|', $count;
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
