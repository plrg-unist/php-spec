#!/usr/bin/env python3
"""Native-first quiet scalar array flags and strict rejection before validation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'quiet-array-flags-and-post-warning-snapshot': br'''<?php
function v76ArrayWarning($level, $message) {
    global $cell, $input, $flag, $calls;
    echo 'H|', $level, '|';
    $calls++;
    $cell = ['tag' => 23];
    $input[90] = 31;
    $flag = '0';
    return true;
}
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$calls = 0;
set_error_handler('v76ArrayWarning', E_WARNING);
echo 'B|';
echo define('V76_FALSE', $input, '0') ? 'T|' : 'BAD|';
$first = constant('V76_FALSE');
$cell = ['tag' => 11];
echo $first['edge']['tag'], '|';
$flag = 2.5;
echo define('V76_TRUE', $input, $flag) ? 'T|' : 'BAD|';
$copy = constant('V76_TRUE');
echo $copy['edge']['tag'], '|', isset($copy[90]) ? 'BAD' : 'split';
echo '|', $input[90], '|';
$copy[] = 19;
echo isset($copy[0]) ? 'zero|' : 'BAD|';
$copy['edge']['tag'] = 41;
$stored = constant('V76_TRUE');
echo $copy['edge']['tag'], '|', $stored['edge']['tag'], '|';
echo define('V76_INT_ZERO', ['tag' => 19], 0) ? 'T|' : 'BAD|';
$integer = constant('V76_INT_ZERO');
echo $integer['tag'], '|', $calls, '|', $flag === '0' ? 'zero|' : 'BAD|';
restore_error_handler();
unset($cell, $input, $first, $copy, $stored, $integer, $flag);
echo 'A|';
''',
    'selected-eval-strict-array-flag-before-cycle-validation': br'''<?php
declare(strict_types=1);
function v76StrictWarning($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD-H|';
    return true;
}
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$flag = 2.5;
$api = 'define';
$calls = 0;
$result = 'kept';
set_error_handler('v76StrictWarning');
echo 'B|';
try {
    eval('declare(strict_types=1); $result = $api(case_insensitive: $flag, value: (($flag = 0) === 0 && ($api = "defined") === "defined" ? $input : []), constant_name: (($cell = $input) ? "V76_STRICT_TYPE" : "BAD"));');
    echo 'BAD-RETURN|';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    $raw = $trace[0]['args'];
    echo 'E|', $e->getMessage(), '|', $trace[0]['function'], '|';
    echo $raw[2] === 2.5 ? 'float|' : 'BAD|';
    echo $raw[1]['edge'] === $raw[1] ? 'cycle|' : 'BAD|';
    $cell = ['tag' => 41];
    echo $raw[1]['edge']['tag'], '|';
    $view = $raw[1];
    $view[] = 53;
    echo isset($view[91]) ? 'history|' : 'BAD|';
    echo $flag, '|', $api, '|', $calls, '|', $result, '|';
    echo defined('V76_STRICT_TYPE') ? 'BAD|' : 'absent|';
    unset($e, $trace, $raw, $view);
}
restore_error_handler();
unset($cell, $input, $flag);
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
