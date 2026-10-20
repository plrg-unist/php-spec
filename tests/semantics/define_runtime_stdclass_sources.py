#!/usr/bin/env python3
"""Native-first ordinary stdClass values with owning properties in DEFINE."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'runtime-stdclass-properties-and-unpinned-duplicate': br'''<?php
class V86Child {
    public int $value = 7;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
function v86Duplicate($level, $message) {
    global $candidate, $api, $calls;
    $calls++;
    echo 'H|', $level, '|';
    $candidate->child->value = 41;
    $candidate = null;
    $api = 'constant';
    return true;
}
$child = new V86Child();
$candidate = new stdClass();
$candidate->child = $child;
$view = (array)$candidate;
$api = 'define';
$calls = 0;
echo 'B|';
$result = $api('V86_DIRECT', $candidate);
echo $result === true ? 'T|' : 'BAD|';
$stored = constant('V86_DIRECT');
echo $stored === $candidate ? 'same|' : 'BAD|';
echo $stored->child->value, '|';
$slot =& $stored->child;
$slot->value = 19;
$view['child'] = null;
echo $view['child'] === null ? 'local-null|' : 'BAD|';
echo $candidate->child->value, '|';
unset($slot, $view, $child, $stored, $candidate);
$candidate = new stdClass();
$candidate->child = new V86Child();
$candidate->child->value = 23;
set_error_handler('v86Duplicate');
$result = $api('V86_DIRECT', $candidate, false);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $candidate === null ? 'null|' : 'BAD|';
echo $api, '|';
$stored = $api('V86_DIRECT');
echo $stored->child->value, '|', $calls, '|';
unset($candidate, $api, $calls, $result, $stored);
echo 'A|';
''',
    'runtime-stdclass-array-snapshot-and-query-cow': br'''<?php
class V86ArrayChild {
    public int $value = 23;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
function v86ArrayName() {
    global $object, $input, $api;
    $object = null;
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V86_ARRAY';
}
$object = new stdClass();
$object->child = new V86ArrayChild();
$cell = ['box' => $object];
$cell[90] = 0;
unset($cell[90]);
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$api = 'define';
echo 'B|';
$result = $api(value: $input, constant_name: v86ArrayName());
echo $result === true ? 'T|' : 'BAD|';
$cell = null;
$copy = constant('V86_ARRAY');
$stored = $copy['edge']['box'];
echo !isset($copy[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
echo $input['edge'] === null && $object === null ? 'null|' : 'BAD|';
echo $api, '|', $stored->child->value, '|';
$bucket =& $copy['edge']['box'];
$bucket = null;
echo $copy['edge']['box'] === null ? 'local-null|' : 'BAD|';
$property =& $stored->child->value;
$property = 41;
$again = constant('V86_ARRAY');
$shared = $again['edge']['box'];
echo $shared === $stored ? 'same|' : 'BAD|';
echo $shared->child->value, '|';
$copy[] = 53;
echo isset($copy[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
unset($bucket, $property, $copy, $again, $shared, $stored, $cell, $input, $object, $api, $result);
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
