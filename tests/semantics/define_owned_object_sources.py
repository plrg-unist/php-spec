#!/usr/bin/env python3
"""Direct owning DEFINE values retain identity beyond captured callee retirement."""
from pathlib import Path

import global_constant_sources as family

DIRECT = 'owned-object-fresh-query-and-normal-argument-retirement'
family.CASES = {
    DIRECT: br'''<?php
class V95Value {
    public int $value = 7;
    public bool $watch = false;
    function __destruct() {
        echo 'D|', $this->value, '|';
        if ($this->watch) {
            global $weak, $destroyed;
            ++$destroyed;
            echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
        }
    }
}
function v95Name() {
    global $call, $payload, $phase, $weak;
    ++$phase;
    if ($phase === 1) {
        $payload->value = 19;
        $call = 'constant';
    } else {
        $payload->value = 41;
        $call = 'defined';
    }
    $payload = null;
    echo 'N|', $phase, '|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return 'V95_DIRECT_OWNED';
}
function v95Report($level, $message) {
    global $weak, $calls;
    ++$calls;
    $old = constant('V95_DIRECT_OWNED');
    echo 'H|', $level, '|', $old->value, '|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return true;
}
$phase = 0;
$calls = 0;
$destroyed = 0;
$payload = new V95Value;
$pointerWeak = WeakReference::create($payload);
$call = define(...);
$weak = WeakReference::create($call);
echo 'B|';
$result = $call(value: $payload, constant_name: v95Name());
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
echo $call, '|', $payload === null ? 'null|' : 'BAD|';
$stored = constant('V95_DIRECT_OWNED');
echo $stored === $pointerWeak->get() ? 'same|' : 'BAD|';
echo $stored->value, '|';
$stored->value = 23;
$again = constant('V95_DIRECT_OWNED');
echo $again === $stored ? 'same|' : 'BAD|';
echo $again->value, '|';
unset($stored, $again, $pointerWeak);
$payload = new V95Value;
$payload->value = 37;
$payload->watch = true;
$call = define(...);
$weak = WeakReference::create($call);
set_error_handler('v95Report');
$result = $call(value: $payload, case_insensitive: false, constant_name: v95Name());
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
$again = constant('V95_DIRECT_OWNED');
echo $call, '|', $again->value, '|', $destroyed, '|', $calls, '|A|';
unset($again, $call, $weak, $payload, $phase, $calls, $destroyed, $result);
''',
    'owned-stdclass-cached-properties-and-direct-query-cow': br'''<?php
class V95StdChild {
    public int $value = 7;
    function __destruct() { echo 'D|', $this->value, '|'; }
}
function v95StdFlag() {
    global $call, $payload, $child, $weak;
    $child->value = 19;
    $child = null;
    $payload = null;
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return false;
}
$child = new V95StdChild;
$payload = new stdClass;
$payload->child = $child;
$initialView = (array)$payload;
unset($initialView);
$pointerWeak = WeakReference::create($payload);
$call = define(...);
$weak = WeakReference::create($call);
echo 'B|';
$result = $call->__invoke('V95_STD_OWNED', $payload, v95StdFlag());
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
echo $payload === null && $child === null ? 'null|' : 'BAD|';
echo $call, '|';
$stored = constant('V95_STD_OWNED');
echo $stored === $pointerWeak->get() ? 'same|' : 'BAD|';
echo $stored->child->value, '|';
$view = (array)$stored;
$view['child'] = null;
echo $view['child'] === null ? 'local-null|' : 'BAD|';
echo $stored->child->value, '|';
$leaf = $stored->child;
$leaf->value = 41;
$again = constant('V95_STD_OWNED');
echo $again === $stored && $again->child === $leaf ? 'same|' : 'BAD|';
echo $again->child->value, '|';
$view[] = 'local';
$againView = (array)$again;
echo isset($view[0]) && !isset($againView[0]) ? 'history|' : 'BAD|';
unset($stored, $view, $leaf, $again, $againView, $call, $weak, $payload, $child, $pointerWeak, $result);
echo 'A|';
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
