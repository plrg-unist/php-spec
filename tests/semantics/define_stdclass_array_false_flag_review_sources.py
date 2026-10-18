#!/usr/bin/env python3
"""Independent three-slot duplicate keeps a captured false flag and original input."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-three-slot-throw-captured-flag-and-input': br'''<?php
const V68_REVIEW_LEFT = new stdClass();
const V68_REVIEW_RIGHT = new stdClass();
const V68_REVIEW_TARGET = 17;
$left = V68_REVIEW_LEFT;
$right = V68_REVIEW_RIGHT;
$left->value = 7;
$right->value = 19;
unset($left, $right);
$cell = V68_REVIEW_LEFT;
$input = ['head' => &$cell, 'nested' => ['leaf' => &$cell]];
function v68ReviewThrow(int $level, string $message): bool {
    global $cell, $flag;
    echo 'H|', $level, '|', constant('V68_REVIEW_TARGET'), '|';
    $cell = V68_REVIEW_RIGHT;
    $flag = true;
    $donor = V68_REVIEW_LEFT;
    $donor->value = 41;
    unset($donor);
    define('V68_REVIEW_SIDE', 31);
    throw new Exception('V68_STOP');
}
set_error_handler('v68ReviewThrow');
$api = 'define';
$flag = false;
$ok = 'kept';
echo 'B|';
try {
    $ok = $api(value: $input, case_insensitive: $flag, constant_name: 'V68_REVIEW_TARGET');
    echo 'BAD|';
} catch (Exception $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo $trace[1]['function'], '|';
    echo $raw['head'] === V68_REVIEW_RIGHT && $raw['nested']['leaf'] === V68_REVIEW_RIGHT ? 'R|' : 'BAD|';
    echo $trace[1]['args'][2] === false ? 'F|' : 'BAD|';
    echo $flag ? 'T|' : 'BAD|';
    echo constant('V68_REVIEW_TARGET'), '|';
    echo V68_REVIEW_LEFT->value, '|', V68_REVIEW_RIGHT->value, '|';
    echo constant('V68_REVIEW_SIDE'), '|', $ok, '|';
    unset($trace, $raw, $error);
}
restore_error_handler();
unset($input, $cell, $flag, $api, $ok);
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
