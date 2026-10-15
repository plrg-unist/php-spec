#!/usr/bin/env python3
"""Native-first duplicate registration while an ignored-warning throw is pending."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-true-pending-duplicate-eligible-handler': br'''<?php
function installThenThrowDuplicate34($level, $message) {
    global $warnings, $effect, $pending;
    echo 'H|', $level, '|';
    $warnings++;
    if ($warnings === 1) {
        define('LiteralPendingDup34', 269);
        $effect = 'after';
        $pending = new Exception('first');
        throw $pending;
    }
    echo 'SECOND|';
    return false;
}
function literalPendingDupCaller34() {
    global $warnings, $effect, $pending;
    $warnings = 0; $effect = 'before'; $pending = null; $result = 99;
    set_error_handler('installThenThrowDuplicate34');
    try {
        $result = define('LiteralPendingDup34', 169, true);
        echo 'NORMAL|';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $warnings, '|', $effect, '|', $result, '|', $e->getMessage();
        echo '|', $e === $pending ? 'I' : 'D';
        echo '|', $e->getPrevious() === null ? 'N' : 'P';
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'LiteralPendingDup34' ? 'N' : 'D';
        echo '|', $trace[1]['args'][1] === 169 ? 'V' : 'D';
        echo '|', $trace[1]['args'][2] === true ? 'T' : 'D';
        echo '|', $trace[2]['function'], '|', constant('LiteralPendingDup34');
        echo '|', defined('literalpendingdup34') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
literalPendingDupCaller34();
''',
    'strict-selected-pending-duplicate-masked-handler': br'''<?php
declare(strict_types=1);
function maskedPendingDup34($level, $message) {
    global $warnings;
    $warnings++; echo 'SECOND|', $level, '|'; return false;
}
function pendingDupValue34() {
    global $candidate, $flag, $call;
    echo 'V|'; $flag = false; $call = 'constant'; return $candidate;
}
function pendingDupName34() {
    global $name, $candidate, $call;
    echo 'N|'; $name = 'later'; $candidate = 'later-value'; $call = 'defined';
    return 'StrictPendingDup34';
}
function installThenMaskDuplicate34($level, $message) {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    echo 'H|', $level, '|'; $warnings++;
    define('StrictPendingDup34', 279);
    set_error_handler('maskedPendingDup34', 8192);
    $name = 'handler'; $candidate = 'handler-value'; $flag = false; $call = 'constant';
    $pending = new Exception('masked-first');
    throw $pending;
}
function strictPendingDupCaller34() {
    global $warnings, $name, $candidate, $flag, $call, $pending;
    $part = 'capture'; $candidate = $part . '-value';
    $warnings = 0; $name = 'StrictPendingDup34'; $flag = true; $call = 'define';
    $pending = null; $result = 99;
    set_error_handler('installThenMaskDuplicate34');
    try {
        $result = $call(case_insensitive: $flag, value: pendingDupValue34(), constant_name: pendingDupName34());
        echo 'NORMAL|';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $warnings, '|', $name, '|', $candidate, '|', $flag === false ? 'F' : 'D';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $e === $pending ? 'I' : 'D';
        echo '|', $e->getPrevious() === null ? 'N' : 'P';
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'StrictPendingDup34' ? 'N' : 'D';
        echo '|', $trace[1]['args'][1] === 'capture-value' ? 'V' : 'D';
        echo '|', $trace[1]['args'][2] === true ? 'T' : 'D';
        echo '|', $trace[2]['function'], '|', constant('StrictPendingDup34');
        echo '|', defined('handler') ? 'T' : 'F';
    } finally {
        restore_error_handler(); restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
strictPendingDupCaller34();
''',
}
family.BASELINE = ('boolean define flag pending-exception registration', b'B|H|2|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
