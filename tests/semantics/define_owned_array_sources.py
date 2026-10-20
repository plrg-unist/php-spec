#!/usr/bin/env python3
"""Owned DEFINE array snapshots retain captured owners through candidate cleanup."""
from pathlib import Path

import global_constant_sources as family


DIRECT = 'owned-array-fresh-query-and-normal-candidate-retirement'
family.CASES = {
    DIRECT: br'''<?php
class V94Child {
    public int $value = 0;
    public bool $watch = false;
    function __destruct() {
        echo 'D|', $this->value, '|';
        if ($this->watch) {
            global $weak, $destroyed;
            ++$destroyed;
            echo $weak->get() instanceof Closure ? 'held|' : 'gone|';
        }
    }
}
function v94Name() {
    global $call, $payload, $left, $candidate, $cell, $phase, $weak;
    ++$phase;
    if ($phase === 1) {
        $cell->value = 19;
        $left = null;
        $call = 'constant';
        $payload = [90 => 31];
    } else {
        $cell->value = 41;
        $candidate = null;
        $call = 'defined';
        $payload = [90 => 53];
    }
    echo 'N|', $phase, '|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD|';
    return 'V94_ARRAY_OWNED';
}
function v94Report($level, $message) {
    global $cell, $weak, $calls, $destroyed;
    ++$calls;
    $cell = null;
    $saved = constant('V94_ARRAY_OWNED');
    echo 'H|', $level, '|', $saved['edge']->value, '|', $destroyed, '|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD|';
    return true;
}
$phase = 0;
$calls = 0;
$destroyed = 0;
$call = define(...);
$weak = WeakReference::create($call);
$left = new V94Child();
$left->value = 7;
$cell = $left;
$payload = ['edge' => &$cell];
$payload[90] = 7;
unset($payload[90]);
$raw = $payload;
echo 'B|';
$result = $call(value: $payload, constant_name: v94Name());
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD|';
echo $call, '|', $payload[90], '|';
$cell = null;
$stored = constant('V94_ARRAY_OWNED');
$object = $stored['edge'];
echo $object->value, '|';
$stored['edge'] = null;
$object->value = 23;
$again = constant('V94_ARRAY_OWNED');
echo $again['edge'] === $object ? 'same|' : 'BAD|';
echo $again['edge']->value, '|';
$stored[] = 'query';
$raw[] = 'raw';
echo isset($stored[0]) && isset($raw[91]) && $raw['edge'] === null ? 'history|' : 'BAD|';
unset($stored, $again, $object, $raw, $payload, $cell);
$call = define(...);
$weak = WeakReference::create($call);
$candidate = new V94Child();
$candidate->value = 37;
$candidate->watch = true;
$cell = $candidate;
$payload = ['edge' => &$cell];
set_error_handler('v94Report');
$result = $call(value: $payload, case_insensitive: false, constant_name: v94Name());
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD|';
$again = constant('V94_ARRAY_OWNED');
echo $call, '|', $payload[90], '|', $again['edge']->value, '|', $destroyed, '|', $calls, '|A|';
unset($again, $call, $weak, $payload, $cell, $candidate, $left, $phase, $calls, $destroyed, $result);
''',
    'owned-array-explicit-nested-alias-snapshot-and-query-cow': br'''<?php
function v94ArrayFlag() {
    global $call, $weak, $cell, $input;
    $call = 'defined';
    $cell = 23;
    $input[90] = 31;
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD|';
    return false;
}
$call = define(...);
$weak = WeakReference::create($call);
$cell = 7;
$input = ['edge' => &$cell, 'nested' => ['leaf' => &$cell]];
$input[90] = 7;
unset($input[90]);
$raw = $input;
echo 'B|';
$result = $call->__invoke('V94_NESTED_OWNED', $input, v94ArrayFlag());
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD|';
$cell = 41;
$stored = constant('V94_NESTED_OWNED');
echo $call, '|', $stored['edge'], '|', $stored['nested']['leaf'], '|', $raw['edge'], '|', $input[90], '|';
$stored['nested']['leaf'] = null;
$stored['edge'] = null;
$again = constant('V94_NESTED_OWNED');
echo $again['edge'], '|', $again['nested']['leaf'], '|';
$stored[] = 'query';
$raw[] = 'raw';
echo isset($stored[0]) && isset($raw[91]) && $raw['nested']['leaf'] === 41 ? 'history|' : 'BAD|';
echo 'A|';
unset($call, $weak, $cell, $input, $raw, $stored, $again, $result);
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|N|1|held|')
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
