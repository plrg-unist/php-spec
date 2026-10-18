#!/usr/bin/env python3
"""Independent captured quiet flag and pending certified-object registration."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'captured-string-flag-and-pending-object-publication': br'''<?php
class V80ReviewBox {
    public int $value = 0;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
const V80_REVIEW_LEFT = new V80ReviewBox();
const V80_REVIEW_RIGHT = new V80ReviewBox();
$left = V80_REVIEW_LEFT;
$right = V80_REVIEW_RIGHT;
$left->value = 17;
$right->value = 23;
unset($left, $right);
function v80ReviewName() {
    global $candidate, $flag, $api;
    $candidate = V80_REVIEW_RIGHT;
    $flag = '0';
    $api = 'defined';
    echo 'N|';
    return 'V80_REVIEW_TARGET';
}
function v80ReviewWarning($level, $message) {
    global $candidate, $flag, $calls;
    $calls++;
    echo 'H|', $level, '|';
    echo $flag === '0' ? 'zero|' : 'BAD|';
    echo $candidate === V80_REVIEW_RIGHT ? 'R|' : 'BAD|';
    echo !defined('V80_REVIEW_TARGET') ? 'absent|' : 'BAD|';
    $left = V80_REVIEW_LEFT;
    $left->value = 41;
    throw new Exception('V80_PENDING');
}
echo 'B|';
$calls = 0;
$candidate = V80_REVIEW_LEFT;
$prefix = 'fal';
$flag = $prefix . 'se';
unset($prefix);
$api = 'define';
$result = 'kept';
set_error_handler('v80ReviewWarning', E_WARNING);
try {
    $result = $api(case_insensitive: $flag, value: $candidate, constant_name: v80ReviewName());
    echo 'BAD_RETURN|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $frame = $trace[1];
    $args = $frame['args'];
    echo 'E|', $error->getMessage(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $frame['function'] === 'define' ? 'define|' : 'BAD|';
    echo $args[2] === 'false' ? 'raw|' : 'BAD|';
    echo $args[1] === V80_REVIEW_LEFT ? 'left|' : 'BAD|';
    echo defined('V80_REVIEW_TARGET') ? 'defined|' : 'BAD|';
    $held = constant('V80_REVIEW_TARGET');
    echo $held === V80_REVIEW_LEFT ? 'same|' : 'BAD|';
    $slot =& $held->value;
    $slot = 53;
    unset($slot, $held);
    echo V80_REVIEW_LEFT->value, '|', $result, '|', $calls, '|';
    unset($args, $frame, $trace, $error);
}
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
            Path(stem).parent.name == 'captured-string-flag-and-pending-object-publication'):
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
