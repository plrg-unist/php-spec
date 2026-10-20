#!/usr/bin/env python3
"""Ordinary method Closure as the only path to an unpinned receiver."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'method-closure-private-array-owner-retires-before-catch': br'''<?php
class V85ReviewOwner {
    public int $value = 7;
    public function read() {
        global $reads;
        $reads++;
        $this->value = 41;
        return $this->value;
    }
    public function __destruct() {
        global $destroyed;
        $destroyed++;
        echo 'D|', $this->value, '|';
    }
}
function v85ReviewName() {
    global $owner, $closure, $input, $api;
    $owner = null;
    $closure = null;
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V85_REVIEW_OLD';
}
function v85ReviewReport($level, $message) {
    global $cell, $calls;
    $calls++;
    $seen = $cell();
    $cell = null;
    echo 'H|', $level, '|', $seen, '|', constant('V85_REVIEW_OLD'), '|';
    throw new Exception('V85_STOP');
}
define('V85_REVIEW_OLD', 17);
$destroyed = 0;
$reads = 0;
$calls = 0;
$owner = new V85ReviewOwner();
$closure = $owner->read(...);
$cell = $closure;
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$api = 'define';
$result = 'kept';
set_error_handler('v85ReviewReport');
echo 'B|';
try {
    $result = $api(value: $input, case_insensitive: false, constant_name: v85ReviewName());
    echo 'BAD_RETURN|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $frame = $trace[1];
    $args = $frame['args'];
    $raw = $args[1];
    echo 'E|', $error->getMessage(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $frame['function'], '|';
    echo $args[2] === false ? 'false|' : 'BAD|';
    echo $raw['edge'] === null && $cell === null ? 'null|' : 'BAD|';
    echo $owner === null && $closure === null ? 'dropped|' : 'BAD|';
    echo $api, '|', constant('V85_REVIEW_OLD'), '|', $calls, '|', $reads, '|', $destroyed, '|', $result, '|';
    echo $input[90], '|';
    echo !isset($args[1][90]) ? 'split|' : 'BAD|';
    $raw[] = 53;
    echo isset($raw[91]) && !isset($args[1][91]) ? 'history|' : 'BAD|';
    unset($raw, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($cell, $input, $owner, $closure, $api, $result, $calls, $reads, $destroyed);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and Path(stem).parent.name ==
            'method-closure-private-array-owner-retires-before-catch'):
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
