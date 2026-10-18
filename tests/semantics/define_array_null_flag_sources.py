#!/usr/bin/env python3
"""Native-first NULL array flags, receive callbacks and strict pre-body errors."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'null-deprecation-repairs-cycle-and-selects-late-duplicate': br'''<?php
function v77ArrayReceive($level, $message) {
    global $cell, $input, $flag, $api, $mode, $deprecations, $warnings;
    if ($level === E_DEPRECATED) {
        echo 'D|', $level, '|';
        $deprecations++;
        if ($mode === 1) {
            $cell = ['tag' => 23];
            $input[90] = 31;
            $flag = true;
        } else {
            $cell = ['tag' => 29];
            define('V77_DUPLICATE', 17);
            $flag = false;
            $api = 'defined';
        }
        return true;
    }
    echo 'W|', $level, '|';
    $warnings++;
    $cell = ['tag' => 41];
    return true;
}
$cell = [];
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$cell = $input;
$flag = null;
$api = 'define';
$mode = 1;
$deprecations = 0;
$warnings = 0;
set_error_handler('v77ArrayReceive');
echo 'B|';
echo define('V77_FRESH', $input, $flag) ? 'T|' : 'BAD|';
$copy = constant('V77_FRESH');
echo $copy['edge']['tag'], '|', isset($copy[90]) ? 'BAD|' : 'split|';
echo $input[90], '|', $flag === true ? 'true|' : 'BAD|';
$copy[] = 19;
echo isset($copy[0]) ? 'zero|' : 'BAD|';
$copy['edge']['tag'] = 53;
$stored = constant('V77_FRESH');
echo $copy['edge']['tag'], '|', $stored['edge']['tag'], '|';
unset($input[90]);
$mode = 2;
$flag = null;
$result = 'kept';
$result = $api(case_insensitive: $flag, value: $input, constant_name: 'V77_DUPLICATE');
echo $result === false ? 'F|' : 'BAD|';
echo constant('V77_DUPLICATE'), '|', $cell['tag'], '|', $api, '|';
echo $deprecations, '|', $warnings, '|', $flag === false ? 'false|' : 'BAD|';
restore_error_handler();
unset($cell, $input, $copy, $stored, $flag);
echo 'A|';
''',
    'null-deprecation-creates-cycle-before-duplicate': br'''<?php
function v77CreateCycle($level, $message) {
    global $cell, $input, $flag, $api, $calls;
    echo 'D|', $level, '|';
    $calls++;
    $cell = $input;
    $flag = true;
    $api = 'defined';
    return true;
}
define('V77_CYCLE', 17);
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$flag = null;
$api = 'define';
$calls = 0;
$result = 'kept';
set_error_handler('v77CreateCycle');
echo 'B|';
try {
    $result = $api(case_insensitive: $flag, value: $input, constant_name: 'V77_CYCLE');
    echo 'BAD-RETURN|';
} catch (ValueError $e) {
    $trace = $e->getTrace();
    $raw = $trace[0]['args'];
    echo 'E|', $e->getMessage(), '|', $trace[0]['function'], '|';
    echo $raw[2] === null ? 'null|' : 'BAD|';
    echo $raw[1]['edge'] === $raw[1] ? 'cycle|' : 'BAD|';
    $cell = ['tag' => 41];
    echo $raw[1]['edge']['tag'], '|';
    $view = $raw[1];
    $view[] = 53;
    echo isset($view[91]) ? 'history|' : 'BAD|';
    echo constant('V77_CYCLE'), '|', $calls, '|';
    echo $flag === true ? 'true|' : 'BAD|';
    echo $api, '|', $result, '|';
    unset($e, $trace, $raw, $view);
}
restore_error_handler();
unset($cell, $input, $flag);
echo 'A|';
''',
    'selected-eval-strict-null-before-captured-cycle': br'''<?php
declare(strict_types=1);
function v77StrictReceive($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD-H|';
    return true;
}
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$flag = null;
$api = 'define';
$calls = 0;
$result = 'kept';
set_error_handler('v77StrictReceive');
echo 'B|';
try {
    eval('declare(strict_types=1); $result = $api(case_insensitive: $flag, value: (($flag = true) === true && ($api = "defined") === "defined" ? $input : []), constant_name: (($cell = $input) ? "V77_STRICT_NULL" : "BAD"));');
    echo 'BAD-RETURN|';
} catch (TypeError $e) {
    $trace = $e->getTrace();
    $raw = $trace[0]['args'];
    echo 'E|', $e->getMessage(), '|', $trace[0]['function'], '|';
    echo $raw[2] === null ? 'null|' : 'BAD|';
    echo $raw[1]['edge'] === $raw[1] ? 'cycle|' : 'BAD|';
    $cell = ['tag' => 41];
    echo $raw[1]['edge']['tag'], '|';
    $view = $raw[1];
    $view[] = 53;
    echo isset($view[91]) ? 'history|' : 'BAD|';
    echo $flag === true ? 'true|' : 'BAD|';
    echo $api, '|', $calls, '|', $result, '|';
    echo defined('V77_STRICT_NULL') ? 'BAD|' : 'absent|';
    unset($e, $trace, $raw, $view);
}
restore_error_handler();
unset($cell, $input, $flag);
echo 'A|';
''',
}
family.BASELINE = ('null define flag reception', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
