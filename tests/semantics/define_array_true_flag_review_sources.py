#!/usr/bin/env python3
"""Ignored-flag callback repairs a cycle before a late duplicate snapshot."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'warning-repairs-cycle-installs-key-and-duplicate-throw': br'''<?php
$cell = [];
$input = ['edge' => &$cell];
$cell = $input;
$stage = 0;
$flag = true;
function v74ReviewWarning(int $level, string $message): bool {
    global $cell, $stage, $flag;
    $stage = $stage + 1;
    echo 'H|', $stage, '|', $level, '|';
    if ($stage === 1) {
        $flag = false;
        $cell = ['leaf' => 23];
        echo define('V74_REVIEW_ROW', 17) ? 'T|' : 'BAD|';
        return true;
    }
    $cell = ['leaf' => 31];
    throw new Exception('V74_STOP');
}
set_error_handler('v74ReviewWarning');
$api = 'define';
$ok = 'kept';
echo 'B|';
try {
    $ok = $api(value: $input, case_insensitive: $flag, constant_name: 'V74_REVIEW_ROW');
    echo 'BAD|';
} catch (Exception $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo $trace[1]['function'], '|';
    echo $trace[1]['args'][2] === true ? 'true|' : 'BAD|';
    echo $flag === false ? 'false|' : 'BAD|';
    echo $raw['edge']['leaf'], '|', constant('V74_REVIEW_ROW'), '|', $stage, '|', $ok, '|';
    $bucket =& $raw['edge'];
    $bucket = ['leaf' => 41];
    echo $input['edge']['leaf'], '|';
    unset($bucket, $raw, $trace, $error);
}
restore_error_handler();
unset($input, $cell, $stage, $flag, $api, $ok);
echo 'A|';
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
