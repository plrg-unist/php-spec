#!/usr/bin/env python3
"""Independent abrupt duplicate disposal keeps the original input in its trace."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-array-duplicate-throw-original-input-trace': br'''<?php
const V67_REVIEW_LEFT = new stdClass();
const V67_REVIEW_RIGHT = new stdClass();
const V67_REVIEW_TARGET = 17;
$left = V67_REVIEW_LEFT;
$right = V67_REVIEW_RIGHT;
$left->value = 7;
$right->value = 19;
unset($left, $right);
$cell = V67_REVIEW_LEFT;
$input = ['head' => &$cell, 'nested' => ['leaf' => &$cell]];
function v67ReviewThrow(int $level, string $message): bool {
    global $cell;
    echo 'H|', $level, '|', constant('V67_REVIEW_TARGET'), '|';
    $cell = V67_REVIEW_RIGHT;
    $donor = V67_REVIEW_LEFT;
    $donor->value = 41;
    unset($donor);
    define('V67_REVIEW_SIDE', 31);
    throw new Exception('V67_STOP');
}
set_error_handler('v67ReviewThrow');
$api = 'define';
$ok = 'kept';
echo 'B|';
try {
    $ok = $api(value: $input, constant_name: 'V67_REVIEW_TARGET');
    echo 'BAD|';
} catch (Exception $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo $trace[1]['function'], '|';
    echo $raw['head'] === V67_REVIEW_RIGHT && $raw['nested']['leaf'] === V67_REVIEW_RIGHT ? 'R|' : 'BAD|';
    echo constant('V67_REVIEW_TARGET'), '|';
    echo V67_REVIEW_LEFT->value, '|', V67_REVIEW_RIGHT->value, '|';
    echo constant('V67_REVIEW_SIDE'), '|', $ok, '|';
    unset($trace, $raw, $error);
}
restore_error_handler();
unset($input, $cell, $api, $ok);
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
