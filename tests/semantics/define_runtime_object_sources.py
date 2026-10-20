#!/usr/bin/env python3
"""Native-first ordinary runtime objects in direct and array DEFINE values."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'runtime-object-publication-and-unpinned-duplicate': br'''<?php
class V84Box {
    public int $value = 7;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
function v84Duplicate($level, $message) {
    global $candidate, $api, $calls;
    $calls++;
    echo 'H|', $level, '|';
    $candidate->value = 41;
    $candidate = null;
    $api = 'constant';
    return true;
}
$candidate = new V84Box();
$api = 'define';
$calls = 0;
echo 'B|';
$result = $api('V84_DIRECT', $candidate);
echo $result === true ? 'T|' : 'BAD|';
$stored = constant('V84_DIRECT');
echo $stored === $candidate ? 'same|' : 'BAD|';
echo $stored->value, '|';
$slot =& $stored->value;
$slot = 19;
echo $candidate->value, '|';
unset($slot, $stored, $candidate);
$candidate = new V84Box();
$candidate->value = 23;
set_error_handler('v84Duplicate');
$result = $api('V84_DIRECT', $candidate, false);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $candidate === null ? 'null|' : 'BAD|';
echo $api, '|';
$stored = $api('V84_DIRECT');
echo $stored->value, '|', $calls, '|';
unset($candidate, $api, $calls, $result, $stored);
echo 'A|';
''',
    'runtime-object-array-source-retirement-and-query-cow': br'''<?php
class V84ArrayBox {
    public int $value = 23;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
function v84ArrayName() {
    global $object, $input, $api;
    $object = null;
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V84_ARRAY';
}
$object = new V84ArrayBox();
$cell = ['object' => $object];
$cell[90] = 0;
unset($cell[90]);
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$api = 'define';
echo 'B|';
$result = $api(value: $input, constant_name: v84ArrayName());
echo $result === true ? 'T|' : 'BAD|';
$cell = null;
$copy = constant('V84_ARRAY');
$stored = $copy['edge']['object'];
echo !isset($copy[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
echo $input['edge'] === null && $object === null ? 'null|' : 'BAD|';
echo $api, '|', $stored->value, '|';
$slot =& $copy['edge']['object'];
$slot = null;
echo $copy['edge']['object'] === null ? 'local-null|' : 'BAD|';
$property =& $stored->value;
$property = 41;
$again = constant('V84_ARRAY');
$shared = $again['edge']['object'];
echo $shared === $stored ? 'same|' : 'BAD|';
echo $shared->value, '|';
$copy[] = 53;
echo isset($copy[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
unset($slot, $property, $copy, $again, $shared, $stored, $cell, $input, $object, $api, $result);
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
