#!/usr/bin/env python3
"""Native-first duplicate define of case-insensitive special names."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-special-duplicates-preserve-true-false-null': br'''<?php
echo 'B|';
echo define('true', 853) ? 'BAD' : 'F', '|', constant('TRUE') === true ? 'T' : 'BAD';
echo '|', define('FaLsE', 857, false) ? 'BAD' : 'F', '|', constant('false') === false ? 'F' : 'BAD';
echo '|', define('NULL', 859, false) ? 'BAD' : 'F', '|', constant('nUlL') === null ? 'N' : 'BAD';
''',
    'captured-special-name-and-false-flag-before-live-effects': br'''<?php
function specialValue44() {
    global $name, $candidate, $flag, $call;
    echo 'V|'; $name = 'value-name44'; $candidate = 997; $flag = true; $call = 'constant';
    $part = 'outer'; return $part . '-value44';
}
function reportSpecial44($level, $message) {
    global $name, $candidate, $flag, $call, $count;
    echo 'H|', $level, '|', $message, '|'; $count++;
    define('SpecialSibling44', 887);
    $name = 'handler-name44'; $candidate = 777; $flag = true; $call = 'defined';
    return false;
}
function specialCaller44() {
    global $name, $candidate, $flag, $call, $count;
    $part = 'tR'; $name = $part . 'uE'; $candidate = 0; $flag = false;
    $call = 'define'; $count = 0; $result = 99;
    set_error_handler('reportSpecial44');
    try {
        $result = $call(case_insensitive: $flag, constant_name: $name, value: specialValue44());
        echo $result === false ? 'F' : 'BAD', '|', constant('TrUe') === true ? 'T' : 'BAD';
        echo '|', constant('SpecialSibling44'), '|', $name, '|', $candidate, '|', $flag === true ? 'T' : 'BAD', '|', $call, '|', $count;
        echo '|', defined('handler-name44') ? 'BAD' : 'F';
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; specialCaller44();
''',
    'strict-special-duplicate-after-all-argument-effects': br'''<?php
declare(strict_types=1);
function strictSpecialValue44() { global $call; echo 'V|'; $call = 'constant'; return 889; }
function strictSpecialName44() { global $call; echo 'N|'; $call = 'defined'; $part = 'FaL'; return $part . 'sE'; }
function strictSpecialHandler44($level, $message) { global $count; echo 'H|', $level, '|', $message, '|'; $count++; return true; }
$call = 'define'; $result = 99; $count = 0;
set_error_handler('strictSpecialHandler44');
echo 'B|';
$result = $call(value: strictSpecialValue44(), constant_name: strictSpecialName44(), case_insensitive: false);
restore_error_handler();
echo $result === false ? 'F' : 'BAD', '|', constant('FALSE') === false ? 'F' : 'BAD', '|', $call, '|', $count;
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
