#!/usr/bin/env python3
"""Pending-cycle suppression preserves the original Previous chain and caller aliases."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'pending-cycle-existing-row-and-previous-chain': br'''<?php
const V75_REVIEW_OLD = 17;
$stage = 0;
$flag = true;
function v75ReviewPending(int $level, string $message): bool {
    global $stage, $flag, $cell, $input, $api;
    $stage = $stage + 1;
    echo 'H|', $stage, '|', $level, '|';
    $flag = false;
    $api = 'defined';
    $cell = $input;
    define('V75_REVIEW_SIDE', 31);
    $base = new Exception('V75_BASE');
    throw new Exception('V75_PENDING', 0, $base);
}
set_error_handler('v75ReviewPending');
echo 'B|';
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$api = 'define';
$result = 'kept';
try {
    $result = $api(value: $input, case_insensitive: $flag, constant_name: 'V75_REVIEW_OLD');
} catch (Exception $error) {
    $base = $error->getPrevious();
    $trace = $error->getTrace();
    $baseTrace = $base->getTrace();
    $raw = $trace[1]['args'][1];
    echo 'E|', $error->getMessage(), '|', $base->getMessage(), '|';
    echo $base->getPrevious() === null ? 'none|' : 'bad|';
    echo $trace[1]['function'], '|', $trace[1]['args'][2] ? 'true|' : 'false|';
    echo $baseTrace[1]['args'][2] ? 'true|' : 'false|';
    echo $flag ? 'true|' : 'false|';
    echo V75_REVIEW_OLD, '|', V75_REVIEW_SIDE, '|', $stage, '|', $result, '|';
    $cell = ['tag' => 23];
    $bucket =& $raw['edge'];
    $bucket = ['tag' => 41];
    echo $input['edge']['tag'], '|', $baseTrace[1]['args'][1]['edge']['tag'], '|';
    unset($bucket);
}
restore_error_handler();
$ok = define('V75_REVIEW_RECOVERY', $input, false);
echo $ok ? 'T|' : 'F|';
$copy = constant('V75_REVIEW_RECOVERY');
$copy['edge']['tag'] = 53;
echo $copy['edge']['tag'], '|', constant('V75_REVIEW_RECOVERY')['edge']['tag'], '|';
$cell['tag'] = 67;
echo $input['edge']['tag'], '|', constant('V75_REVIEW_RECOVERY')['edge']['tag'], '|';
unset($copy, $error, $base, $trace, $baseTrace, $raw, $input, $cell);
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
