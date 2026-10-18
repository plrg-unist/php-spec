#!/usr/bin/env python3
"""Native-first true/NULL flags with completed certified object captures."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'normal-object-warning-null-and-late-duplicate': br'''<?php
class V79Box {
    public int $value = 0;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
const V79_LEFT = new V79Box();
const V79_RIGHT = new V79Box();
$left = V79_LEFT;
$right = V79_RIGHT;
$left->value = 7;
$right->value = 19;
unset($left, $right);
function v79Report($level, $message) {
    global $candidate, $flag, $mode, $calls;
    $calls = $calls + 1;
    echo 'H|', $calls, '|', $level, '|';
    $left = V79_LEFT;
    $right = V79_RIGHT;
    if ($mode === 'true') {
        $candidate = V79_RIGHT;
        $flag = false;
        $left->value = 11;
    } elseif ($mode === 'null-fresh') {
        $candidate = V79_RIGHT;
        $flag = true;
        $left->value = 41;
    } elseif ($mode === 'true-duplicate') {
        if ($flag === true) {
            $candidate = V79_LEFT;
            $flag = false;
            $right->value = 37;
        } else {
            $right->value = 43;
        }
    } elseif ($level === E_DEPRECATED) {
        $candidate = V79_LEFT;
        $flag = true;
        $right->value = 23;
        define('V79_LATE', 17);
    } else {
        $right->value = 31;
    }
    return true;
}
echo 'B|';
$calls = 0;
$mode = 'true';
$flag = true;
$candidate = V79_LEFT;
set_error_handler('v79Report', E_WARNING | E_DEPRECATED);
echo define(value: $candidate, constant_name: 'V79_TRUE', case_insensitive: $flag) ? 'T|' : 'BAD|';
$row = constant('V79_TRUE');
echo $row === V79_LEFT ? 'left|' : 'BAD|';
echo $row->value, '|';
echo $candidate === V79_RIGHT ? 'R|' : 'BAD|';
echo $flag === false ? 'false|' : 'BAD|';
unset($row);
$mode = 'null-fresh';
$flag = null;
$candidate = V79_LEFT;
echo define(value: $candidate, constant_name: 'V79_NULL', case_insensitive: $flag) ? 'T|' : 'BAD|';
$row = constant('V79_NULL');
echo $row === V79_LEFT && $row === constant('V79_TRUE') ? 'same|' : 'BAD|';
echo $row->value, '|';
echo $flag === true ? 'true|' : 'BAD|';
unset($row);
$mode = 'null-duplicate';
$flag = null;
$candidate = V79_RIGHT;
echo define(value: $candidate, constant_name: 'V79_LATE', case_insensitive: $flag) ? 'BAD|' : 'F|';
echo constant('V79_LATE'), '|', V79_RIGHT->value, '|';
$mode = 'true-duplicate';
$flag = true;
$candidate = V79_RIGHT;
echo define(value: $candidate, constant_name: 'V79_TRUE', case_insensitive: $flag) ? 'BAD|' : 'F|';
$row = constant('V79_TRUE');
echo $row === V79_LEFT ? 'old|' : 'BAD|';
echo $row->value, '|', V79_RIGHT->value, '|';
echo $flag === false ? 'false|' : 'BAD|';
echo $calls, '|';
unset($row);
restore_error_handler();
unset($candidate, $flag, $mode, $calls);
echo 'A|';
''',
    'selected-eval-strict-null-object-before-deprecated': br'''<?php
declare(strict_types=1);
const V79_STRICT_LEFT = new stdClass();
const V79_STRICT_RIGHT = new stdClass();
$left = V79_STRICT_LEFT;
$right = V79_STRICT_RIGHT;
$left->value = 7;
$right->value = 19;
unset($left, $right);
function v79Never($level, $message) {
    global $calls;
    $calls = $calls + 1;
    echo 'BAD_HANDLER|';
    return true;
}
function v79StrictName() {
    global $candidate, $flag, $api;
    $candidate = V79_STRICT_RIGHT;
    $flag = true;
    $api = 'defined';
    $left = V79_STRICT_LEFT;
    $left->value = 43;
    return 'V79_STRICT';
}
echo 'B|';
$calls = 0;
$candidate = V79_STRICT_LEFT;
$flag = null;
$api = 'define';
$result = 'kept';
set_error_handler('v79Never', E_WARNING | E_DEPRECATED);
try {
    eval('declare(strict_types=1); $result = $api(case_insensitive: $flag, value: $candidate, constant_name: v79StrictName()); echo "BAD_RETURN|";');
} catch (TypeError $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $frame = $trace[0];
    $args = $frame['args'];
    $captured = $args[1];
    echo $frame['function'] === 'define' ? 'define|' : 'BAD|';
    echo $args[2] === null ? 'null|' : 'BAD|';
    echo $captured === V79_STRICT_LEFT ? 'left|' : 'BAD|';
    echo $candidate === V79_STRICT_RIGHT ? 'right|' : 'BAD|';
    echo $flag === true && $api === 'defined' ? 'changed|' : 'BAD|';
    echo $captured->value, '|', $calls, '|';
    echo $result === 'kept' ? 'kept|' : 'BAD|';
    echo !defined('V79_STRICT') ? 'absent|' : 'BAD|';
    unset($captured, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($candidate, $flag, $api, $result, $calls);
echo 'A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and
            Path(stem).parent.name == 'normal-object-warning-null-and-late-duplicate'):
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '90']
        timeout = 105
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
