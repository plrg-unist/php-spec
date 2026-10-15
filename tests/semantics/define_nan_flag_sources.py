#!/usr/bin/env python3
"""Native-first NaN define flag reception and the later ignored-flag warning."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-nan-flag-publication-and-duplicate': br'''<?php
echo 'B|';
echo define('LiteralNanFlag35', 193, NAN) ? 'T' : 'F';
echo '|', constant('LiteralNanFlag35'), '|';
echo define('LiteralNanFlag35', 194, NAN) ? 'T' : 'F';
echo '|', constant('LiteralNanFlag35');
''',
    'captured-nan-flag-and-later-warning-throw': br'''<?php
function nanFlagValue35() {
    global $flag, $call;
    echo 'V|'; $flag = false; $call = 'constant'; return 197;
}
function nanFlagName35() {
    global $flag, $call;
    echo 'N|'; $flag = 0; $call = 'defined'; return 'CapturedNanFlag35';
}
function reportNanFlag35($level, $message) {
    global $name, $value, $flag, $call, $warnings, $saved;
    echo 'H|', $level, '|', $message, '|';
    $warnings++;
    if ($warnings === 1) {
        define('CapturedNanFlag35', 297);
        $name = 'changed'; $value = 997; $flag = false; $call = 'constant';
        return false;
    }
    $flag = null; $call = 'defined';
    $saved = new Exception('later'); throw $saved;
}
function nanFlagCaller35() {
    global $name, $value, $flag, $call, $warnings, $saved;
    $name = 'CapturedNanFlag35'; $value = 197; $flag = NAN; $call = 'define';
    $warnings = 0; $saved = null; $result = 99;
    set_error_handler('reportNanFlag35');
    try {
        $result = $call(case_insensitive: $flag, value: nanFlagValue35(), constant_name: nanFlagName35());
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        $raw = $trace[1]['args'][2];
        echo $e === $saved ? 'S' : 'BAD', '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $raw !== $raw ? 'N' : 'BAD', '|', $trace[1]['args'][0];
        echo '|', $trace[1]['args'][1], '|', $warnings, '|', $result;
        echo '|', $name, '|', $value, '|', $flag === null ? 'Z' : 'BAD', '|', $call;
        echo '|', constant('CapturedNanFlag35');
    } finally { restore_error_handler(); echo '|F'; }
}
echo 'B|'; nanFlagCaller35();
''',
    'strict-nan-flag-after-all-argument-effects': br'''<?php
declare(strict_types=1);
function strictNanValue35() { global $flag, $call; echo 'V|'; $flag = false; $call = 'constant'; return 199; }
function strictNanName35() { global $call; echo 'N|'; $call = 'defined'; return 'StrictNanFlag35'; }
function strictNanHandler35($level, $message) { echo 'BAD-H|'; return true; }
$flag = NAN; $call = 'define'; $result = 99;
set_error_handler('strictNanHandler35');
echo 'B|';
try {
    $result = $call(case_insensitive: $flag, value: strictNanValue35(), constant_name: strictNanName35());
    echo 'BAD';
} catch (TypeError $e) {
    $trace = $e->getTrace(); $raw = $trace[0]['args'][2];
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $raw !== $raw ? 'N' : 'BAD', '|', $trace[0]['args'][0], '|', $trace[0]['args'][1];
}
restore_error_handler();
echo '|', $call, '|', $flag === false ? 'F' : 'BAD', '|', $result;
echo '|', defined('StrictNanFlag35') ? 'BAD' : 'U';
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
