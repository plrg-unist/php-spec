#!/usr/bin/env python3
"""Raw request-string flags survive pending duplicate array cleanup."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'raw-request-flag-pending-duplicate-and-trace-alias': br'''<?php
$stage = 0;
function v76ReviewFlag(int $level, string $message): bool {
    global $stage, $flag, $api, $cell, $input;
    $stage = $stage + 1;
    echo 'H|', $stage, '|', $level, '|';
    $flag = '0';
    $api = 'constant';
    $cell = ['tag' => 23];
    $input[90] = 'caller';
    define('V76_REVIEW_ROW', 17);
    define('V76_REVIEW_SIDE', 31);
    throw new Exception('V76_PENDING');
}
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 'removed';
unset($input[90]);
$part = 'fal';
$flag = $part . 'se';
unset($part);
$api = 'define';
$result = 'kept';
set_error_handler('v76ReviewFlag');
echo 'B|';
try {
    $result = $api(case_insensitive: $flag, value: $input, constant_name: 'V76_REVIEW_ROW');
    echo 'BAD|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo 'E|', $error->getMessage(), '|', $trace[1]['function'], '|';
    echo $trace[1]['args'][2] === 'false' ? 'raw|' : 'BAD|';
    echo $flag === '0' ? 'zero|' : 'BAD|';
    echo $api, '|', $raw['edge']['tag'], '|';
    echo isset($raw[90]) ? 'BAD|' : 'split|';
    echo $input[90], '|', V76_REVIEW_ROW, '|', V76_REVIEW_SIDE, '|', $stage, '|', $result, '|';
    $bucket =& $raw['edge'];
    $bucket = ['tag' => 41];
    echo $input['edge']['tag'], '|', $trace[1]['args'][1]['edge']['tag'], '|';
    unset($bucket);
    $raw[] = 'trace';
    echo isset($raw[91]) ? 'history|' : 'BAD|';
}
restore_error_handler();
unset($raw, $trace, $error, $input, $cell, $flag, $api, $result, $stage);
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
