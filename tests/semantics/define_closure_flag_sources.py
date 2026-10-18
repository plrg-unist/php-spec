#!/usr/bin/env python3
"""Native-first live Closure DEFINE flags reject before body work."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'lexical-closure-flag-before-cycle-and-duplicate': br'''<?php
function v82Never($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD_HANDLER|';
    return true;
}
function v82Name() {
    global $input, $flag, $api, $cell;
    echo 'N|';
    $cell = 23;
    $flag = false;
    $input[90] = 31;
    $api = 'defined';
    return 'V82_OLD';
}
define('V82_OLD', 17);
$valueCell = [];
$input = ['edge' => &$valueCell];
$valueCell = $input;
$cell = 7;
$invocations = 0;
$flag = function () use (&$cell) {
    global $invocations;
    $invocations++;
    return $cell;
};
$api = 'define';
$calls = 0;
$result = 'kept';
set_error_handler('v82Never');
echo 'B|';
try {
    $result = $api(case_insensitive: $flag, value: $input, constant_name: v82Name());
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $frame = $trace[0];
    $args = $frame['args'];
    $captured = $args[1];
    $rawFlag = $args[2];
    echo 'E|', $error->getMessage(), '|', $frame['function'], '|';
    echo $captured['edge'] === $captured ? 'cycle|' : 'BAD|';
    echo !isset($captured[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
    echo $flag === false ? 'false|' : 'BAD|';
    echo $api, '|', constant('V82_OLD'), '|', $calls, '|', $invocations, '|', $result, '|';
    echo $rawFlag(), '|';
    $cell = 41;
    echo $rawFlag(), '|', $invocations, '|';
    $valueCell = ['tag' => 43];
    echo $captured['edge']['tag'], '|';
    unset($rawFlag, $captured, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($valueCell, $input, $cell, $flag, $api, $result, $calls, $invocations);
echo 'A|';
''',
    'strict-named-closure-flag-retains-object-value': br'''<?php
declare(strict_types=1);
const V82_LEFT = new stdClass();
const V82_RIGHT = new stdClass();
$left = V82_LEFT;
$left->value = 7;
unset($left);
function v82StrictFlag() {
    global $invocations;
    $invocations++;
    return 19;
}
function v82StrictNever($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD_HANDLER|';
    return true;
}
function v82StrictName() {
    global $candidate, $flag, $api;
    $candidate = V82_RIGHT;
    $flag = true;
    $api = 'defined';
    $left = V82_LEFT;
    $left->value = 43;
    return 'V82_STRICT';
}
$candidate = V82_LEFT;
$flag = v82StrictFlag(...);
$api = 'define';
$calls = 0;
$invocations = 0;
$result = 'kept';
set_error_handler('v82StrictNever');
echo 'B|';
try {
    eval('declare(strict_types=1); $result = $api(case_insensitive: $flag, value: $candidate, constant_name: v82StrictName());');
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $frame = $trace[0];
    $args = $frame['args'];
    $captured = $args[1];
    $rawFlag = $args[2];
    echo 'E|', $error->getMessage(), '|', $frame['function'], '|';
    echo $captured === V82_LEFT ? 'left|' : 'BAD|';
    echo $candidate === V82_RIGHT ? 'right|' : 'BAD|';
    echo $flag === true ? 'true|' : 'BAD|';
    echo $api, '|', $captured->value, '|', $calls, '|', $invocations, '|', $result, '|';
    echo !defined('V82_STRICT') ? 'absent|' : 'BAD|';
    echo $rawFlag(), '|', $invocations, '|';
    unset($rawFlag, $captured, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($candidate, $flag, $api, $result, $calls, $invocations);
echo 'A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|N|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
