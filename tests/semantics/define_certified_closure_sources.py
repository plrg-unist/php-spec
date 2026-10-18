#!/usr/bin/env python3
"""Native-first certified Closure publication and array snapshot identity."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'direct-closure-publication-and-normal-duplicate': br'''<?php
const V83_LEFT = static function () {
    static $counter = 7;
    return ++$counter;
};
const V83_RIGHT = static function () {
    static $counter = 17;
    return ++$counter;
};
function v83Duplicate($level, $message) {
    global $candidate, $api, $calls;
    $calls++;
    $candidate = V83_LEFT;
    $api = 'constant';
    $right = V83_RIGHT;
    echo 'H|', $level, '|', $right(), '|';
    return true;
}
$candidate = V83_LEFT;
$api = 'define';
$calls = 0;
echo 'B|';
$result = $api('V83_DIRECT', $candidate);
echo $result === true ? 'T|' : 'BAD|';
$stored = constant('V83_DIRECT');
echo $stored === V83_LEFT ? 'left|' : 'BAD|';
echo $stored(), '|';
unset($stored);
$candidate = V83_RIGHT;
set_error_handler('v83Duplicate');
$result = $api('V83_DIRECT', $candidate, false);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $candidate === V83_LEFT ? 'left|' : 'BAD|';
echo $api, '|';
$stored = constant('V83_DIRECT');
$right = V83_RIGHT;
echo $stored === V83_LEFT ? 'old|' : 'BAD|';
echo $stored(), '|', $right(), '|', $calls, '|';
unset($candidate, $api, $calls, $result, $stored, $right);
echo 'A|';
''',
    'nested-closure-alias-snapshot-and-query-cow': br'''<?php
const V83_ARRAY_LEFT = static function () {
    static $counter = 7;
    return ++$counter;
};
const V83_ARRAY_RIGHT = static function () {
    static $counter = 17;
    return ++$counter;
};
function v83ArrayName() {
    global $cell, $input, $api;
    $cell = ['call' => V83_ARRAY_RIGHT];
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V83_ARRAY';
}
$cell = ['call' => V83_ARRAY_LEFT];
$cell[90] = 0;
unset($cell[90]);
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$api = 'define';
echo 'B|';
$result = $api(value: $input, constant_name: v83ArrayName());
echo $result === true ? 'T|' : 'BAD|';
$cell = ['call' => V83_ARRAY_LEFT];
$copy = constant('V83_ARRAY');
$stored = $copy['edge']['call'];
echo $stored === V83_ARRAY_RIGHT ? 'right|' : 'BAD|';
echo !isset($copy[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
echo $input['edge']['call'] === V83_ARRAY_LEFT ? 'left|' : 'BAD|';
echo $api, '|', $stored(), '|';
$slot =& $copy['edge']['call'];
$slot = V83_ARRAY_LEFT;
$local = $copy['edge']['call'];
echo $local(), '|';
$again = constant('V83_ARRAY');
$shared = $again['edge']['call'];
echo $shared === V83_ARRAY_RIGHT ? 'right|' : 'BAD|';
echo $shared(), '|';
$copy[] = 53;
echo isset($copy[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
unset($slot, $copy, $again, $stored, $local, $shared, $cell, $input, $api, $result);
echo 'A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|')
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
