#!/usr/bin/env python3
"""Throwing NULL-flag deprecation cancels the fresh array DEFINE body."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'throwing-deprecated-cancels-fresh-copy-and-keeps-raw-trace': br'''<?php
$calls = 0;
function v77ReviewDeprecated(int $level, string $message): bool {
    global $calls, $flag, $api, $cell, $input;
    $calls = $calls + 1;
    echo 'H|', $calls, '|', $level, '|';
    $flag = true;
    $api = 'defined';
    $cell = ['tag' => 23];
    $input[90] = 'caller';
    define('V77_REVIEW_SIDE', 31);
    throw new Exception('V77_CANCEL');
}
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 'removed';
unset($input[90]);
$flag = null;
$api = 'define';
$result = 'kept';
set_error_handler('v77ReviewDeprecated');
echo 'B|';
try {
    $result = $api(case_insensitive: $flag, value: $input, constant_name: 'V77_REVIEW_CANCEL');
    echo 'BAD|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo 'E|', $error->getMessage(), '|', $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[1]['function'], '|', $trace[1]['args'][2] === null ? 'null|' : 'BAD|';
    echo $flag === true ? 'true|' : 'BAD|';
    echo $api, '|', $raw['edge']['tag'], '|';
    echo isset($raw[90]) ? 'BAD|' : 'split|';
    echo $input[90], '|', defined('V77_REVIEW_CANCEL') ? 'BAD|' : 'absent|';
    echo V77_REVIEW_SIDE, '|', $calls, '|', $result, '|';
    $bucket =& $raw['edge'];
    $bucket = ['tag' => 41];
    echo $input['edge']['tag'], '|', $trace[1]['args'][1]['edge']['tag'], '|';
    unset($bucket);
    $raw[] = 'trace';
    echo isset($raw[91]) ? 'history|' : 'BAD|';
}
restore_error_handler();
unset($raw, $trace, $error, $input, $cell, $flag, $api, $result, $calls);
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
