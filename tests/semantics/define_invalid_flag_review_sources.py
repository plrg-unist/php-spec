#!/usr/bin/env python3
"""Independent unpinned object-flag trace ownership before DEFINE body entry."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'object-flag-trace-retains-unpinned-instance': br'''<?php
class V81ReviewValue {
    public int $value = 0;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
class V81ReviewFlag {
    public int $value = 0;
    public function __destruct() { echo 'F|', $this->value, '|'; }
}
const V81_REVIEW_LEFT = new V81ReviewValue();
const V81_REVIEW_RIGHT = new V81ReviewValue();
$left = V81_REVIEW_LEFT;
$right = V81_REVIEW_RIGHT;
$left->value = 17;
$right->value = 23;
unset($left, $right);
function v81ReviewName() {
    global $candidate, $flag, $api;
    $oldFlag = $flag;
    $oldFlag->value = 41;
    $flag = false;
    $candidate = V81_REVIEW_RIGHT;
    $api = 'defined';
    unset($oldFlag);
    echo 'N|';
    return 'V81_REVIEW_TARGET';
}
function v81ReviewNever($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD_HANDLER|';
    return true;
}
$flag = new V81ReviewFlag();
$flag->value = 7;
$candidate = V81_REVIEW_LEFT;
$api = 'define';
$calls = 0;
$result = 'kept';
set_error_handler('v81ReviewNever');
echo 'B|';
try {
    $result = $api(case_insensitive: $flag, value: $candidate, constant_name: v81ReviewName());
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $frame = $trace[0];
    $args = $frame['args'];
    $rawFlag = $args[2];
    $captured = $args[1];
    echo 'E|', $error->getMessage(), '|', $frame['function'], '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $captured === V81_REVIEW_LEFT ? 'left|' : 'BAD|';
    echo $candidate === V81_REVIEW_RIGHT ? 'right|' : 'BAD|';
    echo $flag === false ? 'false|' : 'BAD|';
    echo $rawFlag->value, '|';
    $slot =& $rawFlag->value;
    $slot = 53;
    unset($slot);
    $captured->value = 31;
    echo $args[2]->value, '|', V81_REVIEW_LEFT->value, '|', $calls, '|', $result, '|';
    echo !defined('V81_REVIEW_TARGET') ? 'absent|' : 'BAD|';
    unset($rawFlag, $captured, $args, $frame, $trace);
    echo 'kept-trace|';
    unset($error);
}
echo 'released|';
restore_error_handler();
unset($candidate, $flag, $api, $result, $calls);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and
            Path(stem).parent.name == 'object-flag-trace-retains-unpinned-instance'):
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
