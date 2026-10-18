#!/usr/bin/env python3
"""Raw pooled-array string flags survive capture, COW and a pending Warning."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'raw-string-flag-capture-and-pending-fresh-snapshot': br'''<?php
$calls = 0;
function v78ReviewWarning(int $level, string $message): bool {
    global $calls, $flags, $api, $cell, $input;
    $calls++;
    echo 'H|', $calls, '|', $level, '|';
    $flags[1] = '';
    $api = 'defined';
    $cell = ['tag' => 23];
    $input[90] = 'caller';
    define('V78_REVIEW_SIDE', 31);
    throw new Exception('V78_PENDING');
}
$flags = ['0', 'false', ''];
$savedFlags = $flags;
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 'removed';
unset($input[90]);
$api = 'define';
$result = 'kept';
set_error_handler('v78ReviewWarning');
echo 'B|';
try {
    $result = $api(case_insensitive: $flags[1], value: (($flags[1] = '0') === '0' ? $input : []), constant_name: 'V78_REVIEW_PENDING');
    echo 'BAD|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo 'E|', $error->getMessage(), '|', $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[1]['function'], '|', $trace[1]['args'][2] === 'false' ? 'raw|' : 'BAD|';
    echo $flags[1] === '' ? 'empty|' : 'BAD|', $savedFlags[1] === 'false' ? 'saved|' : 'BAD|';
    echo $api, '|', $result, '|', V78_REVIEW_SIDE, '|';
    $stored = constant('V78_REVIEW_PENDING');
    echo $stored['edge']['tag'], '|', isset($stored[90]) ? 'BAD|' : 'split|';
    echo $raw['edge']['tag'], '|', $input[90], '|';
    $cell = ['tag' => 41];
    echo $raw['edge']['tag'], '|', $stored['edge']['tag'], '|';
    $copy = constant('V78_REVIEW_PENDING');
    $bucket =& $copy['edge'];
    $bucket['tag'] = 53;
    unset($bucket);
    $copy[] = 'query';
    $view = $raw;
    $view[] = 'trace';
    echo $copy['edge']['tag'], '|', $stored['edge']['tag'], '|';
    echo isset($copy[0]) ? 'zero|' : 'BAD|', isset($view[91]) ? 'history|' : 'BAD|';
}
restore_error_handler();
unset($raw, $trace, $error, $input, $cell, $flags, $savedFlags, $api, $result, $calls, $stored, $copy, $view);
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
