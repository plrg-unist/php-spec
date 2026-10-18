#!/usr/bin/env python3
"""Independent late-created and late-broken define input recursion."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-cycle-created-and-cut-after-value-capture': br'''<?php
const V71_REVIEW_TARGET = 17;
$cell = [];
$input = ['edge' => &$cell, 'again' => &$cell];
$warnings = 0;
function v71UnexpectedWarning($level, $message) {
    global $warnings;
    $warnings++;
    echo 'BAD-H|';
    return true;
}
set_error_handler('v71UnexpectedWarning');
$api = 'define';
$ok = 'kept';
echo 'B|';
try {
    $ok = $api(value: $input, case_insensitive: ($cell = $input) === null, constant_name: 'V71_REVIEW_TARGET');
    echo 'BAD|';
} catch (ValueError $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $raw = $trace[0]['args'][1];
    echo $trace[0]['function'], '|';
    echo $trace[0]['args'][2] === false ? 'false|' : 'BAD|';
    echo isset($raw['edge']['edge']) ? 'cycle|' : 'BAD|';
    echo constant('V71_REVIEW_TARGET'), '|', $warnings, '|', $ok, '|';
    $cell = ['tag' => 23];
    echo $raw['edge']['tag'] === 23 && $raw['again']['tag'] === 23 ? 'broken|' : 'BAD|';
    $cell = $input;
    echo $api(value: $input, case_insensitive: ($cell = ['tag' => 23]) === null, constant_name: 'V71_REVIEW_RECOVER') ? 'T|' : 'BAD|';
    $copy = constant('V71_REVIEW_RECOVER');
    $copy['edge']['tag'] = 31;
    echo $copy['edge']['tag'], '|', $copy['again']['tag'], '|', $cell['tag'], '|';
    echo constant('V71_REVIEW_RECOVER')['edge']['tag'] === 23 ? 'stored|' : 'BAD|';
    unset($trace, $raw, $error, $copy);
}
restore_error_handler();
unset($input, $cell, $warnings, $api, $ok);
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
