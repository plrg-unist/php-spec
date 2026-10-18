#!/usr/bin/env python3
"""Independent rejected method Closure and its unpinned receiver lifetime."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'method-closure-flag-retains-unpinned-receiver': br'''<?php
class V82ReviewOwner {
    public int $value = 7;
    public function read() {
        global $reads;
        $reads++;
        echo 'C|';
        return $this->value;
    }
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
const V82_REVIEW_LEFT = new stdClass();
const V82_REVIEW_RIGHT = new stdClass();
function v82ReviewName() {
    global $owner, $candidate, $flag, $api;
    $owner->value = 41;
    $owner = null;
    $candidate = V82_REVIEW_RIGHT;
    $flag = false;
    $api = 'defined';
    echo 'N|';
    return 'V82_REVIEW_TARGET';
}
function v82ReviewNever($level, $message) {
    global $warnings;
    $warnings++;
    echo 'BAD_HANDLER|';
    return true;
}
$owner = new V82ReviewOwner();
$flag = $owner->read(...);
$candidate = V82_REVIEW_LEFT;
$api = 'define';
$reads = 0;
$warnings = 0;
$result = 'kept';
set_error_handler('v82ReviewNever');
echo 'B|';
try {
    $result = $api(case_insensitive: $flag, value: $candidate, constant_name: v82ReviewName());
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $frame = $trace[0];
    $args = $frame['args'];
    $raw = $args[2];
    $captured = $args[1];
    echo 'E|', $error->getMessage(), '|', $frame['function'], '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $captured === V82_REVIEW_LEFT ? 'left|' : 'BAD|';
    echo $candidate === V82_REVIEW_RIGHT ? 'right|' : 'BAD|';
    echo $flag === false ? 'false|' : 'BAD|';
    echo $owner === null ? 'null|' : 'BAD|';
    echo $api, '|', $reads, '|', $warnings, '|', $result, '|';
    echo !defined('V82_REVIEW_TARGET') ? 'absent|' : 'BAD|';
    echo $raw(), '|', $reads, '|';
    unset($raw, $captured, $args, $frame, $trace);
    echo 'kept-trace|';
    unset($error);
}
echo 'released|';
restore_error_handler();
unset($candidate, $flag, $owner, $api, $reads, $warnings, $result);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and
            Path(stem).parent.name == 'method-closure-flag-retains-unpinned-receiver'):
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
