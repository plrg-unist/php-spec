#!/usr/bin/env python3
"""Native-first byte-only array flags from compiled literal-array elements."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'pooled-byte-flags-and-normal-duplicate-snapshot': br'''<?php
function v78ByteWarning($level, $message) {
    global $calls, $cell, $input, $flags;
    $calls++;
    echo 'H|', $calls, '|', $level, '|';
    if ($calls === 1) {
        $cell = ['tag' => 23];
        $input[90] = 31;
        $flags[1] = '';
    } else {
        $cell = ['tag' => 41];
    }
    return true;
}
$flags = ['0', 'false', ''];
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$calls = 0;
$api = 'define';
set_error_handler('v78ByteWarning');
echo 'B|';
echo define('V78_ROW', $input, $flags[0]) ? 'T|' : 'BAD|';
$first = constant('V78_ROW');
echo $first['edge']['tag'], '|';
$result = $api(case_insensitive: $flags[1], value: (($flags[1] = '0') === '0' ? $input : []), constant_name: 'V78_ROW');
echo $result === false ? 'F|' : 'BAD|';
$stored = constant('V78_ROW');
echo $stored['edge']['tag'], '|', $cell['tag'], '|';
echo isset($stored[90]) ? 'BAD|' : 'split|';
echo $input[90], '|', $flags[1] === '' ? 'empty|' : 'BAD|';
echo define('V78_EMPTY', ['tag' => 19], $flags[2]) ? 'T|' : 'BAD|';
$empty = constant('V78_EMPTY');
echo $empty['tag'], '|', $calls, '|';
restore_error_handler();
unset($input, $cell, $flags, $first, $stored, $empty);
echo 'A|';
''',
    'selected-eval-strict-byte-flag-before-cycle': br'''<?php
declare(strict_types=1);
function v78StrictByteWarning($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD-H|';
    return true;
}
$flags = ['false'];
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$calls = 0;
$api = 'define';
$result = 'kept';
set_error_handler('v78StrictByteWarning');
echo 'B|';
try {
    eval('declare(strict_types=1); $result = $api(case_insensitive: $flags[0], value: (($flags[0] = "0") === "0" && ($api = "defined") === "defined" ? $input : []), constant_name: (($cell = $input) ? "V78_STRICT_BYTES" : "BAD"));');
    echo 'BAD-RETURN|';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    $raw = $trace[0]['args'];
    echo 'E|', $e->getMessage(), '|', $trace[0]['function'], '|';
    echo $raw[2] === 'false' ? 'raw|' : 'BAD|';
    echo $flags[0] === '0' ? 'zero|' : 'BAD|';
    echo $raw[1]['edge'] === $raw[1] ? 'cycle|' : 'BAD|';
    $cell = ['tag' => 41];
    echo $raw[1]['edge']['tag'], '|';
    $view = $raw[1];
    $view[] = 53;
    echo isset($view[91]) ? 'history|' : 'BAD|';
    echo $api, '|', $calls, '|', $result, '|';
    echo defined('V78_STRICT_BYTES') ? 'BAD|' : 'absent|';
    unset($e, $trace, $raw, $view);
}
restore_error_handler();
unset($input, $cell, $flags);
echo 'A|';
''',
}
family.BASELINE = ('scalar define flag reception', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
