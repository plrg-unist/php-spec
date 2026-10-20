#!/usr/bin/env python3
"""Native-first bare runtime REAL Closures in direct and array DEFINE values."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'runtime-real-closure-publication-and-normal-duplicate': br'''<?php
function v85RealName() {
    global $candidate, $right, $api, $cell;
    $candidate = $right;
    $api = 'constant';
    $cell = 23;
    echo 'N|';
    return 'V85_REAL';
}
function v85RealDuplicate($level, $message) {
    global $candidate, $cell, $calls;
    $calls++;
    $cell = 41;
    echo 'H|', $level, '|', $candidate(), '|';
    $candidate = null;
    return true;
}
$cell = 7;
$left = static function () use (&$cell) {
    static $count = 0;
    ++$count;
    return $cell + $count;
};
$right = static function () {
    static $count = 100;
    ++$count;
    return $count;
};
$candidate = $left;
$api = 'define';
$calls = 0;
echo 'B|';
$result = $api(value: $candidate, case_insensitive: false, constant_name: v85RealName());
echo $result === true ? 'T|' : 'BAD|';
$stored = $api('V85_REAL');
echo $stored === $left && $candidate === $right ? 'same|' : 'BAD|';
echo $stored(), '|', $left(), '|', $right(), '|';
$api = 'define';
set_error_handler('v85RealDuplicate');
$result = $api('V85_REAL', $candidate, false);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $candidate === null ? 'null|' : 'BAD|';
$again = constant('V85_REAL');
echo $again === $left ? 'same|' : 'BAD|';
echo $again(), '|', $left(), '|', $calls, '|';
unset($stored, $again, $candidate, $left, $right, $api, $calls, $result, $cell);
echo 'A|';
''',
    'runtime-real-closure-array-snapshot-and-query-cow': br'''<?php
function v85RealArrayName() {
    global $cell, $input, $api;
    $cell = 23;
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V85_REAL_ARRAY';
}
$cell = 7;
$slot = static function () use (&$cell) {
    static $count = 0;
    ++$count;
    return $cell + $count;
};
$input = ['edge' => &$slot];
$input[90] = 0;
unset($input[90]);
$api = 'define';
echo 'B|';
$result = $api(value: $input, constant_name: v85RealArrayName());
echo $result === true ? 'T|' : 'BAD|';
$slot = null;
$copy = constant('V85_REAL_ARRAY');
$stored = $copy['edge'];
echo !isset($copy[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
echo $input['edge'] === null ? 'null|' : 'BAD|';
echo $api, '|', $stored(), '|';
$cell = 41;
$bucket =& $copy['edge'];
$bucket = null;
$again = constant('V85_REAL_ARRAY');
$shared = $again['edge'];
echo $copy['edge'] === null ? 'local-null|' : 'BAD|';
echo $shared === $stored ? 'same|' : 'BAD|';
echo $shared(), '|';
$copy[] = 53;
echo isset($copy[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
unset($bucket, $copy, $again, $shared, $stored, $slot, $cell, $input, $api, $result);
echo 'A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|N|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name in family.CASES:
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
