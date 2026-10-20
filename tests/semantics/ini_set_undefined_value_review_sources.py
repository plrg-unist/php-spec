#!/usr/bin/env python3
"""A first argument-read Warning throw cancels later NULL-option reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-first-warning-throw-cancels-null-option-reception': br'''<?php
declare(strict_types=1);
function iniUndefinedValueReviewWarning85($level, $message) {
    global $call, $replacement, $option, $missing, $warningKeep, $warnings, $deprecated, $saved;
    if ($level !== 2) { $deprecated++; echo 'BAD'; return true; }
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $missing = [71]; $warningKeep = $missing;
    $call = $replacement; $option = 'precision';
    ini_set('precision', '10'); define('SOURCE85PEER', 3419);
    $saved = new Exception('undefined-value85-stop'); throw $saved;
}
echo 'B|'; $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$option = null; $warningKeep = null; $warnings = 0; $deprecated = 0;
$saved = null; $result = 99;
set_error_handler('iniUndefinedValueReviewWarning85', 8194);
try { $result = $call->__invoke($option, $missing); echo 'BAD'; }
catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $warnings, '|', $deprecated;
    echo '|', $missing[0], '|', $warningKeep[0], '|', $call === $replacement ? 'S' : 'BAD';
    echo '|', constant('SOURCE85PEER');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '12'), '|', ini_get('precision'), '|', $result;
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
