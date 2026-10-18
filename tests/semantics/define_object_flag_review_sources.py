#!/usr/bin/env python3
"""Certified objects distinguish ignored-Warning publication from NULL cancellation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'captured-object-true-publication-and-null-cancellation': br'''<?php
class V79ReviewBox {
    public int $value = 0;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
const V79_REVIEW_LEFT = new V79ReviewBox();
const V79_REVIEW_RIGHT = new V79ReviewBox();
$init = V79_REVIEW_LEFT;
$init->value = 17;
$init = V79_REVIEW_RIGHT;
$init->value = 23;
unset($init);
$calls = 0;
function v79ReviewReport(int $level, string $message): bool {
    global $calls, $candidate, $flag;
    $calls++;
    echo 'H|', $calls, '|', $level, '|';
    if ($level === E_WARNING) {
        $candidate = V79_REVIEW_RIGHT;
        $flag = false;
        $left = V79_REVIEW_LEFT;
        $left->value = 41;
        throw new Exception('V79_TRUE');
    }
    $candidate = V79_REVIEW_RIGHT;
    $flag = true;
    $left = V79_REVIEW_LEFT;
    $left->value = 53;
    throw new Exception('V79_NULL');
}
$api = 'define';
$candidate = V79_REVIEW_LEFT;
$flag = true;
$result = 'kept';
set_error_handler('v79ReviewReport');
echo 'B|';
try {
    $result = $api(case_insensitive: $flag, value: $candidate, constant_name: 'V79_REVIEW_TRUE');
    echo 'BAD|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    $held = constant('V79_REVIEW_TRUE');
    echo 'E|', $error->getMessage(), '|', $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[1]['function'], '|', $trace[1]['args'][2] === true ? 'true|' : 'BAD|';
    echo $flag === false ? 'now-false|' : 'BAD|';
    echo $raw === V79_REVIEW_LEFT && $held === $raw && $candidate === V79_REVIEW_RIGHT ? 'captured|' : 'BAD|';
    $slot =& $held->value;
    $slot = 43;
    unset($slot);
    echo $raw->value, '|', $result, '|';
    unset($held, $raw, $trace, $error);
}
$candidate = V79_REVIEW_LEFT;
$flag = null;
try {
    $result = $api(case_insensitive: $flag, value: $candidate, constant_name: 'V79_REVIEW_NULL');
    echo 'BAD|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo 'E|', $error->getMessage(), '|', $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[1]['function'], '|', $trace[1]['args'][2] === null ? 'null|' : 'BAD|';
    echo $flag === true ? 'now-true|' : 'BAD|';
    echo $raw === V79_REVIEW_LEFT && $candidate === V79_REVIEW_RIGHT ? 'captured|' : 'BAD|';
    echo defined('V79_REVIEW_NULL') ? 'BAD|' : 'absent|';
    echo $raw->value, '|', $result, '|', $calls, '|';
    unset($raw, $trace, $error);
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
            Path(stem).parent.name == 'captured-object-true-publication-and-null-cancellation'):
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
