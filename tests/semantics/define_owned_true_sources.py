#!/usr/bin/env python3
"""Owned BOOLtrue warnings precede registration while preserving raw captures."""
from pathlib import Path

import global_constant_sources as family

DIRECT = 'owned-true-reentrant-registration-and-raw-trace'
family.CASES = {
    DIRECT: br'''<?php
function v96Name() {
    global $call, $value, $weak;
    $value = 31;
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return 'V96_OWNED_TRUE';
}
function v96Report($level, $message) {
    global $calls, $snapshot, $value, $weak;
    ++$calls;
    echo 'H|', $level, '|', $calls, '|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    if ($calls === 1) {
        $observed = new Exception('OBSERVE');
        $snapshot = $observed->getTrace();
        unset($observed);
        $value = 41;
        define('V96_OWNED_TRUE', 53);
        echo 'I|', constant('V96_OWNED_TRUE'), '|';
    } else {
        echo 'O|', constant('V96_OWNED_TRUE'), '|';
    }
    return true;
}
$value = 17;
$calls = 0;
$snapshot = null;
$call = define(...);
$weak = WeakReference::create($call);
set_error_handler('v96Report');
echo 'B|';
$result = $call(value: $value, case_insensitive: true, constant_name: v96Name());
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
$api = $snapshot[1]['args'];
echo $snapshot[0]['function'], '|', $snapshot[1]['function'], '|';
echo $api[0], '|', $api[1], '|';
echo $api[2] === true ? 'true|' : 'BAD|';
echo $call, '|', $value, '|', constant('V96_OWNED_TRUE'), '|', $calls, '|A|';
unset($api, $snapshot, $call, $weak, $value, $calls, $result);
''',
    'owned-true-array-copy-after-warning': br'''<?php
function v96ArrayName() {
    global $call, $input, $cell, $weak;
    $cell = 23;
    $input = [90 => 31];
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return 'V96_ARRAY_TRUE';
}
function v96ArrayReport($level, $message) {
    global $cell, $calls, $weak;
    ++$calls;
    $cell = 41;
    echo 'H|', $level, '|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return true;
}
$cell = 17;
$input = [90 => 0, 'leaf' => &$cell];
unset($input[90]);
$raw = $input;
$calls = 0;
$call = define(...);
$weak = WeakReference::create($call);
set_error_handler('v96ArrayReport');
echo 'B|';
$result = $call(value: $input, case_insensitive: true, constant_name: v96ArrayName());
restore_error_handler();
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
$stored = constant('V96_ARRAY_TRUE');
echo $call, '|', $input[90], '|', $stored['leaf'], '|', $raw['leaf'], '|';
$stored['leaf'] = 0;
$again = constant('V96_ARRAY_TRUE');
echo $stored['leaf'] === 0 ? 'local0|' : 'BAD|';
echo $again['leaf'], '|';
$cell = 53;
$raw[] = 'raw';
$stored[] = 'local';
$fresh = constant('V96_ARRAY_TRUE');
echo $fresh['leaf'], '|', $raw['leaf'], '|';
echo isset($raw[91]) && !isset($raw[0]) && isset($stored[0]) && !isset($fresh[0]) ? 'history|' : 'BAD|';
echo $calls, '|A|';
unset($stored, $again, $fresh, $raw, $input, $cell, $call, $weak, $calls, $result);
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|N|held|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name in family.CASES:
        assert command[-2:] == ['--timeout', '45']
        limit = '180' if Path(stem).parent.name == DIRECT else '120'
        command = [*command[:-1], limit]
        timeout = int(limit) + 15
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
