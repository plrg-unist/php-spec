#!/usr/bin/env python3
"""Native-first named Closure VALUES and shared function static storage."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'named-closure-shared-function-statics-and-normal-duplicate': br'''<?php
function v88Counter() { static $count = 0; ++$count; return $count; }
function v88Other() { static $count = 100; ++$count; return $count; }
function v88Name() {
    global $candidate, $right, $api;
    $candidate = $right;
    $api = 'constant';
    echo 'N|';
    return 'V88_NAMED';
}
function v88Duplicate($level, $message) {
    global $candidate, $calls;
    ++$calls;
    echo 'H|', $level, '|', $candidate(), '|';
    $candidate = null;
    return true;
}
$left = v88Counter(...);
$twin = v88Counter(...);
$right = v88Other(...);
$candidate = $left;
$api = 'define';
$calls = 0;
echo 'B|';
$result = $api(value: $candidate, case_insensitive: false, constant_name: v88Name());
echo $result === true ? 'T|' : 'BAD|';
$stored = $api('V88_NAMED');
echo $stored === $left && $left !== $twin && $candidate === $right ? 'distinct|' : 'BAD|';
echo $stored(), '|', $twin(), '|', v88Counter(), '|', $right(), '|';
$api = 'define';
set_error_handler('v88Duplicate');
$result = $api('V88_NAMED', $candidate, false);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $candidate === null ? 'null|' : 'BAD|';
$again = constant('V88_NAMED');
echo $again === $left ? 'same|' : 'BAD|';
echo v88Counter(), '|', $left(), '|', $calls, '|';
unset($stored, $again, $candidate, $left, $twin, $right, $api, $calls, $result);
echo 'after|', v88Other(), '|A|';
''',
    'named-closure-array-snapshot-query-cow-and-shared-static': br'''<?php
function v88ArrayCounter() { static $count = 0; ++$count; return $count; }
function v88ArrayName() {
    global $input, $api;
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V88_NAMED_ARRAY';
}
$slot = v88ArrayCounter(...);
$twin = v88ArrayCounter(...);
$input = ['edge' => &$slot];
$input[90] = 0;
unset($input[90]);
$api = 'define';
echo 'B|';
$result = $api(value: $input, constant_name: v88ArrayName());
echo $result === true ? 'T|' : 'BAD|';
$slot = null;
$copy = constant('V88_NAMED_ARRAY');
$stored = $copy['edge'];
echo !isset($copy[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
echo $input['edge'] === null ? 'null|' : 'BAD|';
echo $api, '|', $stored(), '|', $twin(), '|', v88ArrayCounter(), '|';
$bucket =& $copy['edge'];
$bucket = null;
$again = constant('V88_NAMED_ARRAY');
$shared = $again['edge'];
echo $copy['edge'] === null ? 'local-null|' : 'BAD|';
echo $shared === $stored ? 'same|' : 'BAD|';
echo $shared(), '|';
$copy[] = 53;
echo isset($copy[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
unset($bucket, $copy, $again, $shared, $stored, $slot, $twin, $input, $api, $result);
echo 'after|', v88ArrayCounter(), '|A|';
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
