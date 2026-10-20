#!/usr/bin/env python3
"""Captured DEFINE NULL flags distinguish strict reception and weak body entry."""
from pathlib import Path

import global_constant_sources as family

DIRECT = 'owned-null-strict-rejection-and-weak-publication'
family.CASES = {
    DIRECT: br'''<?php
declare(strict_types=1);
function v97Name() {
    global $call, $value, $weak;
    $value = 31;
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return 'V97_OWNED_NULL';
}
function v97Flag() {
    global $call, $value, $weak;
    $value = 31;
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return null;
}
function v97Report($level, $message) {
    global $calls, $snapshot, $value, $weak;
    ++$calls;
    $value = 53;
    echo 'H|', $level, '|', $calls, '|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    $observed = new Exception('OBSERVE');
    $snapshot = $observed->getTrace();
    unset($observed);
    return true;
}
$value = 17;
$calls = 0;
$snapshot = null;
$result = 97;
$call = define(...);
$weak = WeakReference::create($call);
set_error_handler('v97Report');
echo 'B|';
try {
    $result = $call(value: $value, case_insensitive: null, constant_name: v97Name());
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $strict = $error->getTrace();
    $args = $strict[0]['args'];
    echo 'S|', $strict[0]['function'], '|', $args[0], '|', $args[1], '|';
    echo $args[2] === null ? 'null|' : 'BAD|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    echo defined('V97_OWNED_NULL') ? 'BAD_ROW|' : 'absent|';
    echo $calls, '|', $result, '|', $value, '|';
    unset($args, $strict, $error);
}
$value = 41;
$call = define(...);
$weak = WeakReference::create($call);
$result = $call->__invoke('V97_OWNED_NULL', $value, v97Flag());
restore_error_handler();
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
$api = $snapshot[1]['args'];
$wrapper = $snapshot[2]['args'];
echo $snapshot[0]['function'], '|', $snapshot[1]['function'], '|', $snapshot[2]['function'], '|';
echo $api[0], '|', $api[1], '|';
echo $api[2] === null ? 'null|' : 'BAD|';
echo $api === $wrapper ? 'rawsame|' : 'BAD|';
echo $call, '|', $value, '|', constant('V97_OWNED_NULL'), '|', $calls, '|A|';
unset($api, $wrapper, $snapshot, $call, $weak, $value, $calls, $result);
''',
    'owned-null-array-copy-after-deprecated': br'''<?php
declare(strict_types=1);
function v97ArrayFlag() {
    global $call, $input, $cell, $weak;
    $cell = 23;
    $input = [90 => 31];
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return null;
}
function v97ArrayReport($level, $message) {
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
set_error_handler('v97ArrayReport');
echo 'B|';
$result = $call->__invoke('V97_ARRAY_NULL', $input, v97ArrayFlag());
restore_error_handler();
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
$stored = constant('V97_ARRAY_NULL');
echo $call, '|', $input[90], '|', $stored['leaf'], '|', $raw['leaf'], '|';
$stored['leaf'] = 0;
$again = constant('V97_ARRAY_NULL');
echo $stored['leaf'] === 0 ? 'local0|' : 'BAD|';
echo $again['leaf'], '|';
$cell = 53;
$raw[] = 'raw';
$stored[] = 'local';
$fresh = constant('V97_ARRAY_NULL');
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
