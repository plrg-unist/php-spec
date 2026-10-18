#!/usr/bin/env python3
"""Independent pending DEFINE publication of the original certified Closure."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'pending-certified-closure-retains-captured-pointer-and-statics': br'''<?php
const V83_REVIEW_LEFT = static function () {
    static $counter = 0;
    return ++$counter;
};
const V83_REVIEW_RIGHT = static function () {
    static $counter = 100;
    return ++$counter;
};
function v83ReviewName() {
    global $flag, $api;
    $flag = false;
    $api = 'defined';
    echo 'N|';
    return 'V83_REVIEW_TARGET';
}
function v83ReviewReport($level, $message) {
    global $candidate, $calls;
    $calls++;
    $candidate = V83_REVIEW_RIGHT;
    $original = V83_REVIEW_LEFT;
    echo 'H|', $level, '|', $original(), '|';
    echo !defined('V83_REVIEW_TARGET') ? 'absent|' : 'BAD|';
    throw new Exception('V83_PENDING');
}
$candidate = V83_REVIEW_LEFT;
$flag = true;
$api = 'define';
$calls = 0;
$result = 'kept';
set_error_handler('v83ReviewReport');
echo 'B|';
try {
    $result = $api(case_insensitive: $flag, value: $candidate, constant_name: v83ReviewName());
    echo 'BAD_RETURN|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $frame = $trace[1];
    $args = $frame['args'];
    $raw = $args[1];
    echo 'E|', $error->getMessage(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $frame['function'], '|';
    echo $args[2] === true ? 'true|' : 'BAD|';
    echo $raw === V83_REVIEW_LEFT ? 'left|' : 'BAD|';
    echo $candidate === V83_REVIEW_RIGHT ? 'right|' : 'BAD|';
    echo $flag === false ? 'false|' : 'BAD|';
    echo $api, '|', $calls, '|', $result, '|';
    $view = constant('V83_REVIEW_TARGET');
    echo $view === $raw ? 'same|' : 'BAD|';
    echo $view(), '|', $raw(), '|';
    $right = V83_REVIEW_RIGHT;
    echo $right(), '|';
    unset($view);
    $again = constant('V83_REVIEW_TARGET');
    echo $again(), '|';
    echo $again === V83_REVIEW_LEFT ? 'same|' : 'BAD|';
    unset($raw, $right, $again, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($candidate, $flag, $api, $calls, $result);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and Path(stem).parent.name ==
            'pending-certified-closure-retains-captured-pointer-and-statics'):
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
