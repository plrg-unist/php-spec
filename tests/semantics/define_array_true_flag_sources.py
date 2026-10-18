#!/usr/bin/env python3
"""Native-first array copying after the ignored true case flag Warning."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'case-warning-before-snapshot-and-recursive-validation': br'''<?php
const V74_LEFT = new stdClass();
const V74_RIGHT = new stdClass();
const V74_OLD = 17;
$left = V74_LEFT;
$right = V74_RIGHT;
$left->value = 17;
$right->value = 23;
unset($left, $right);
function v74Report($level, $message) {
    global $cell, $input, $mode, $calls;
    $calls = $calls + 1;
    echo 'H', $calls, '|';
    if ($mode === 'cycle') {
        $cell = $input;
    } else {
        $cell = V74_RIGHT;
        $input['caller'] = 'case';
    }
    return true;
}
echo 'B|';
$calls = 0;
$mode = 'copy';
$cell = V74_LEFT;
$input = ['head' => &$cell, 'nested' => ['again' => &$cell]];
$input[90] = 'discard';
unset($input[90]);
set_error_handler('v74Report', E_WARNING);
$api = 'define';
echo $api(value: $input, constant_name: 'V74_TREE', case_insensitive: true) ? 'T|' : 'BAD|';
$copy = constant('V74_TREE');
echo $copy['head'] === V74_RIGHT && $copy['nested']['again'] === V74_RIGHT ? 'R|' : 'BAD|';
echo isset($input['caller']) ? 'caller|' : 'BAD|';
echo !isset($copy['caller']) ? 'frozen|' : 'BAD|';
$copy[] = 'query';
echo isset($copy[0]) ? 'zero|' : 'BAD|';
$input[] = 'later';
echo isset($input[91]) ? 'history|' : 'BAD|';
$copy['head']->value = 31;
echo V74_RIGHT->value, '|', V74_LEFT->value, '|';
$bucket =& $copy['nested']['again'];
$bucket = V74_LEFT;
$again = constant('V74_TREE');
echo $again['nested']['again'] === V74_RIGHT ? 'kept|' : 'BAD|';
unset($bucket, $copy, $again);
$mode = 'cycle';
$result = 'kept';
try {
    $result = define('V74_OLD', $input, true);
    echo 'BAD_RETURN|';
} catch (ValueError $error) {
    $cell = V74_RIGHT;
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    echo $trace[0]['args'][2] === true ? 'true|' : 'BAD|';
    echo constant('V74_OLD'), '|', $calls, '|';
    echo $result === 'kept' ? 'kept|' : 'BAD|';
    unset($trace, $error);
}
restore_error_handler();
unset($api, $input, $cell, $mode, $calls, $result);
echo 'A|';
''',
    'selected-eval-fresh-copy-with-pending-handler-exception': br'''<?php
function v74Throw($level, $message) {
    global $cell, $input;
    echo 'H|';
    $cell = ['tag' => 23];
    $input['caller'] = 'case';
    define('V74_EVAL_SIDE', 19);
    throw new Exception('V74_PENDING');
}
echo 'B|';
$cell = ['tag' => 7];
$input = ['edge' => &$cell];
$input[90] = 'discard';
unset($input[90]);
$result = 'kept';
set_error_handler('v74Throw', E_WARNING);
try {
    eval('$api = "define"; $result = $api(value: $input, constant_name: "V74_EVAL_TREE", case_insensitive: true); echo "BAD_RETURN|";');
} catch (Exception $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $frame = $trace[1];
    $args = $frame['args'];
    $captured = $args[1];
    echo $frame['function'] === 'define' ? 'define|' : 'BAD|';
    echo $args[2] === true ? 'true|' : 'BAD|';
    echo !isset($captured['caller']) && isset($input['caller']) ? 'split|' : 'BAD|';
    $row = constant('V74_EVAL_TREE');
    echo $row['edge']['tag'], '|';
    $row[] = 99;
    echo isset($row[0]) ? 'zero|' : 'BAD|';
    $captured[] = 53;
    echo isset($captured[91]) ? 'history|' : 'BAD|';
    $cell = ['tag' => 41];
    echo $captured['edge']['tag'], '|', $row['edge']['tag'], '|', $input['edge']['tag'], '|';
    echo constant('V74_EVAL_SIDE'), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $result === 'kept' ? 'kept|' : 'BAD|';
    unset($row, $captured, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($api, $input, $cell, $result);
echo 'A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
