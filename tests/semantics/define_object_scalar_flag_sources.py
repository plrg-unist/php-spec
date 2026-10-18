#!/usr/bin/env python3
"""Native-first quiet scalar flags with certified object payloads."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'quiet-object-false-and-late-truthy-duplicate': br'''<?php
class V80Box {
    public int $value = 0;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
const V80_LEFT = new V80Box();
const V80_RIGHT = new V80Box();
$left = V80_LEFT;
$right = V80_RIGHT;
$left->value = 7;
$right->value = 19;
unset($left, $right);
function v80Warning($level, $message) {
    global $candidate, $flag, $api, $calls;
    $calls++;
    echo 'H|', $calls, '|', $level, '|';
    $right = V80_RIGHT;
    if ($calls === 1) {
        $candidate = V80_LEFT;
        $flag = '0';
        $api = 'constant';
        $right->value = 23;
        define('V80_LATE', 17);
    } else {
        $right->value = 31;
    }
    return true;
}
echo 'B|';
$calls = 0;
$candidate = V80_LEFT;
$flag = 0;
$api = 'define';
set_error_handler('v80Warning', E_WARNING);
echo define('V80_FALSE', $candidate, $flag) ? 'T|' : 'BAD|';
$row = constant('V80_FALSE');
echo $row === V80_LEFT ? 'left|' : 'BAD|';
echo $row->value, '|';
unset($row);
$candidate = V80_RIGHT;
$flag = 2.5;
$result = $api(value: $candidate, case_insensitive: $flag, constant_name: 'V80_LATE');
echo $result === false ? 'F|' : 'BAD|';
echo constant('V80_LATE'), '|', V80_RIGHT->value, '|';
echo $candidate === V80_LEFT ? 'left|' : 'BAD|';
echo $flag === '0' ? 'zero|' : 'BAD|';
echo $api, '|', $calls, '|';
restore_error_handler();
unset($candidate, $flag, $api, $calls, $result);
echo 'A|';
''',
    'selected-eval-strict-object-string-flag-before-warning': br'''<?php
declare(strict_types=1);
const V80_STRICT_LEFT = new stdClass();
const V80_STRICT_RIGHT = new stdClass();
$left = V80_STRICT_LEFT;
$right = V80_STRICT_RIGHT;
$left->value = 7;
$right->value = 19;
unset($left, $right);
function v80Never($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD_HANDLER|';
    return true;
}
function v80StrictName() {
    global $candidate, $flag, $api;
    $candidate = V80_STRICT_RIGHT;
    $flag = 0;
    $api = 'defined';
    $left = V80_STRICT_LEFT;
    $left->value = 43;
    return 'V80_STRICT';
}
echo 'B|';
$calls = 0;
$candidate = V80_STRICT_LEFT;
$prefix = 'f';
$flag = $prefix . 'alse';
unset($prefix);
$api = 'define';
$result = 'kept';
set_error_handler('v80Never', E_WARNING);
try {
    eval('declare(strict_types=1); $result = $api(case_insensitive: $flag, value: $candidate, constant_name: v80StrictName()); echo "BAD_RETURN|";');
} catch (TypeError $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $frame = $trace[0];
    $args = $frame['args'];
    $captured = $args[1];
    echo $frame['function'] === 'define' ? 'define|' : 'BAD|';
    echo $args[2] === 'false' ? 'raw|' : 'BAD|';
    echo $captured === V80_STRICT_LEFT ? 'left|' : 'BAD|';
    echo $candidate === V80_STRICT_RIGHT ? 'right|' : 'BAD|';
    echo $flag === 0 && $api === 'defined' ? 'changed|' : 'BAD|';
    echo $captured->value, '|', $calls, '|';
    echo $result === 'kept' ? 'kept|' : 'BAD|';
    echo !defined('V80_STRICT') ? 'absent|' : 'BAD|';
    unset($captured, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($candidate, $flag, $api, $result, $calls);
echo 'A|';
''',
}
family.BASELINE = ('scalar define flag reception', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and
            Path(stem).parent.name == 'quiet-object-false-and-late-truthy-duplicate'):
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
