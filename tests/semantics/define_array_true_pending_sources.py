#!/usr/bin/env python3
"""Native-first pending ignored-flag throws before recursive/duplicate arrays."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'pending-warning-then-recursive-value-error': br'''<?php
function v75CycleWarning($level, $message) {
    global $cell, $input, $calls;
    $calls = $calls + 1;
    echo 'H|';
    $cell = $input;
    define('V75_CYCLE_SIDE', 19);
    throw new Exception('V75_PENDING');
}
echo 'B|';
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$calls = 0;
$result = 'kept';
set_error_handler('v75CycleWarning', E_WARNING);
try {
    $result = define('V75_CYCLE', $input, true);
    echo 'BAD_RETURN|';
} catch (Throwable $error) {
    echo 'E|', $error->getMessage(), '|';
    $previous = $error->getPrevious();
    echo $previous === null ? 'none|' : $previous->getMessage() . '|';
    $cell = ['tag' => 41];
    $trace = $error->getTrace();
    $frame = $trace[$previous === null ? 1 : 0];
    $args = $frame['args'];
    $captured = $args[1];
    echo $frame['function'], '|';
    echo $args[2] === true ? 'true|' : 'BAD|';
    echo $captured['edge']['tag'], '|';
    echo !defined('V75_CYCLE') ? 'absent|' : 'BAD|';
    echo constant('V75_CYCLE_SIDE'), '|', $calls, '|';
    echo $result === 'kept' ? 'kept|' : 'BAD|';
    unset($captured, $args, $frame, $trace, $previous, $error);
}
restore_error_handler();
unset($input, $cell, $calls, $result);
echo 'A|';
''',
    'selected-eval-pending-warning-then-array-duplicate': br'''<?php
const V75_DUPLICATE = 17;
function v75DuplicateWarning($level, $message) {
    global $cell, $calls, $flag, $api;
    $calls = $calls + 1;
    echo 'H|';
    $cell = ['tag' => 23];
    $flag = false;
    $api = 'defined';
    define('V75_DUPLICATE_SIDE', 31);
    throw new Exception('V75_DUP_PENDING');
}
echo 'B|';
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 99;
unset($input[90]);
$calls = 0;
$flag = true;
$result = 'kept';
set_error_handler('v75DuplicateWarning', E_WARNING);
try {
    eval('$api = "define"; $result = $api(value: $input, constant_name: "V75_DUPLICATE", case_insensitive: $flag); echo "BAD_RETURN|";');
} catch (Throwable $error) {
    echo 'E|', $error->getMessage(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    $trace = $error->getTrace();
    $frame = $trace[1];
    $args = $frame['args'];
    $captured = $args[1];
    echo $frame['function'], '|';
    echo $args[2] === true && $flag === false ? 'flags|' : 'BAD|';
    echo $api === 'defined' ? 'selected|' : 'BAD|';
    echo $captured['edge']['tag'], '|', constant('V75_DUPLICATE'), '|';
    $captured[] = 53;
    echo isset($captured[91]) ? 'history|' : 'BAD|';
    $cell = ['tag' => 41];
    echo $captured['edge']['tag'], '|', $input['edge']['tag'], '|';
    echo constant('V75_DUPLICATE_SIDE'), '|', $calls, '|';
    echo $result === 'kept' ? 'kept|' : 'BAD|';
    unset($captured, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($input, $cell, $calls, $flag, $api, $result);
echo 'A|';
''',
}
family.BASELINE = ('boolean define flag pending-exception registration', b'B|H|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
