#!/usr/bin/env python3
"""Native-first owning DEFINE flag rejection before the body."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'array-flag-before-cycle-and-duplicate': br'''<?php
function v81Never($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD_HANDLER|';
    return true;
}
function v81ArrayName() {
    global $input, $flag, $api, $flagCell;
    echo 'N|';
    $flagCell = 23;
    $flag = false;
    $input[90] = 31;
    $api = 'defined';
    return 'V81_OLD';
}
define('V81_OLD', 17);
$cell = [];
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$cell = $input;
$flagCell = 7;
$flag = ['ref' => &$flagCell];
$flag[90] = 0;
unset($flag[90]);
$api = 'define';
$calls = 0;
$result = 'kept';
set_error_handler('v81Never');
echo 'B|';
try {
    $result = $api(case_insensitive: $flag, value: $input, constant_name: v81ArrayName());
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
    echo $rawFlag['ref'], '|', $flag === false ? 'false|' : 'BAD|';
    echo $api, '|', constant('V81_OLD'), '|', $calls, '|', $result, '|';
    $cell = ['tag' => 43];
    echo $captured['edge']['tag'], '|';
    $slot =& $rawFlag['ref'];
    $slot = 41;
    echo $flagCell, '|', $trace[0]['args'][2]['ref'], '|';
    $rawFlag[] = 53;
    echo isset($rawFlag[91]) ? 'history|' : 'BAD|';
    unset($slot, $rawFlag, $captured, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($cell, $input, $flag, $flagCell, $api, $result, $calls);
echo 'A|';
''',
    'strict-empty-array-flag-retains-object-value': br'''<?php
declare(strict_types=1);
const V81_LEFT = new stdClass();
const V81_RIGHT = new stdClass();
$left = V81_LEFT;
$left->value = 7;
unset($left);
function v81StrictNever($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD_HANDLER|';
    return true;
}
function v81StrictName() {
    global $candidate, $flag, $api;
    $candidate = V81_RIGHT;
    $flag = true;
    $api = 'defined';
    $left = V81_LEFT;
    $left->value = 43;
    return 'V81_STRICT';
}
$candidate = V81_LEFT;
$flag = [];
$api = 'define';
$calls = 0;
$result = 'kept';
set_error_handler('v81StrictNever');
echo 'B|';
try {
    eval('declare(strict_types=1); $result = $api(case_insensitive: $flag, value: $candidate, constant_name: v81StrictName());');
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $frame = $trace[0];
    $args = $frame['args'];
    $captured = $args[1];
    echo 'E|', $error->getMessage(), '|', $frame['function'], '|';
    echo $args[2] === [] ? 'empty|' : 'BAD|';
    echo $captured === V81_LEFT ? 'left|' : 'BAD|';
    echo $candidate === V81_RIGHT ? 'right|' : 'BAD|';
    echo $flag === true ? 'true|' : 'BAD|';
    echo $api, '|', $captured->value, '|', $calls, '|', $result, '|';
    echo !defined('V81_STRICT') ? 'absent|' : 'BAD|';
    unset($captured, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($candidate, $flag, $api, $result, $calls);
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
