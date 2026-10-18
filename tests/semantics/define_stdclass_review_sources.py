#!/usr/bin/env python3
"""Independent selected define capture and shared duplicate callback identity."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-captured-object-and-duplicate-handler': br'''<?php
const V65_REVIEW_LEFT = new stdClass();
const V65_REVIEW_RIGHT = new stdClass();
$left = V65_REVIEW_LEFT;
$right = V65_REVIEW_RIGHT;
$left->value = 17;
$right->value = 23;
unset($left, $right);
function v65ReviewDuplicate(int $level, string $message): bool {
    $old = constant('V65_REVIEW_DYN');
    echo 'H|', $old === V65_REVIEW_LEFT ? 'L|' : 'BAD|';
    $old->value = 53;
    throw new Exception('V65_STOP');
}
echo 'B|';
$payload = V65_REVIEW_LEFT;
$api = 'define';
$result = $api(
    value: $payload,
    constant_name: (($payload = V65_REVIEW_RIGHT) === V65_REVIEW_RIGHT
        ? 'V65_REVIEW_DYN' : 'BAD'),
    case_insensitive: false
);
echo $result ? 'T|' : 'F|';
$old = constant('V65_REVIEW_DYN');
echo $old === V65_REVIEW_LEFT ? 'L|' : 'BAD|';
echo $payload === V65_REVIEW_RIGHT ? 'R|' : 'BAD|';
$slot =& $old->value;
$slot = 41;
echo V65_REVIEW_LEFT->value, '|', V65_REVIEW_RIGHT->value, '|';
unset($slot, $old);
set_error_handler('v65ReviewDuplicate', E_WARNING);
$payload = V65_REVIEW_RIGHT;
try {
    $result = $api(constant_name: 'V65_REVIEW_DYN', value: $payload);
    echo 'BAD|';
} catch (Exception $error) {
    echo 'E|', $error->getMessage(), '|';
    unset($error);
}
restore_error_handler();
echo constant('V65_REVIEW_DYN') === V65_REVIEW_LEFT ? 'L|' : 'BAD|';
echo V65_REVIEW_LEFT->value, '|', V65_REVIEW_RIGHT->value, '|';
unset($payload, $api, $result);
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
