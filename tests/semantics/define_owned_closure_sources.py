#!/usr/bin/env python3
"""Retained intrinsic DEFINE calls preserve captured owners and durable selection."""
from pathlib import Path

import global_constant_sources as family


DIRECT = 'owned-define-capture-fresh-query-and-normal-duplicate'
family.CASES = {
    DIRECT: br'''<?php
function v93Name() {
    global $call, $value, $phase;
    ++$phase;
    if ($phase === 1) {
        $call = 'defined';
        $value = 31;
    } else {
        $call = 'constant';
        $value = 53;
    }
    echo 'N|', $phase, '|';
    return 'V93_OWNED';
}
function v93Report($level, $message) {
    global $calls, $value;
    ++$calls;
    echo 'H|', $level, '|', constant('V93_OWNED'), '|', $value, '|';
    return true;
}
$call = define(...);
$value = 17;
$phase = 0;
$calls = 0;
echo 'B|';
$result = $call(value: $value, case_insensitive: false, constant_name: v93Name());
echo $result === true ? 'T|' : 'BAD|';
echo constant('V93_OWNED'), '|', $call, '|', $value, '|';
$call = define(...);
$value = 41;
set_error_handler('v93Report');
$result = $call(value: $value, case_insensitive: false, constant_name: v93Name());
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo constant('V93_OWNED'), '|', $call, '|', $value, '|', $calls, '|A|';
unset($call, $value, $phase, $calls, $result);
''',
    'owned-define-same-site-replay-after-frame-and-owner-retirement': br'''<?php
function v93Repeat($key, $payload) {
    $callee = define(...);
    $reply = $callee($key, $payload);
    $callee = null;
    echo 'R|';
    return $reply;
}
function v93RepeatReport($level, $message) {
    global $calls;
    ++$calls;
    echo 'H|', $level, '|', constant('V93_REPEAT'), '|';
    return true;
}
$calls = 0;
echo 'B|';
$result = v93Repeat('V93_REPEAT', 23);
echo $result === true ? 'T|' : 'BAD|';
echo constant('V93_REPEAT'), '|';
set_error_handler('v93RepeatReport');
$result = v93Repeat('V93_REPEAT', 31);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo constant('V93_REPEAT'), '|', $calls, '|A|';
unset($calls, $result);
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|N|1|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name in family.CASES:
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '120']
        timeout = 135
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
