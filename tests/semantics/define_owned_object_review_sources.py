#!/usr/bin/env python3
"""Direct trace arguments outlive a captured DEFINE callee, then retire payload."""
from pathlib import Path

import global_constant_sources as family


CASE = 'owned-define-direct-object-trace-outlives-callee'
family.CASES = {
    CASE: br'''<?php
const V95_REVIEW_DIRECT = 17;
class V95ReviewPayload {
    public int $value = 7;
    function __destruct() {
        global $weak, $destroyed;
        ++$destroyed;
        echo 'D|', $this->value, '|';
        echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    }
}
function v95ReviewFlag() {
    global $call, $payload, $cell, $weak;
    $cell->value = 31;
    $payload = null;
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return false;
}
function v95ReviewReport($level, $message) {
    global $cell, $calls, $weak, $chosen;
    ++$calls;
    $cell->value = 41;
    $cell = null;
    echo 'H|', $level, '|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    $chosen = new Exception('STOP');
    throw $chosen;
}
$payload = new V95ReviewPayload;
$cell = $payload;
$call = define(...);
$weak = WeakReference::create($call);
$calls = 0;
$destroyed = 0;
$result = 97;
$chosen = null;
set_error_handler('v95ReviewReport');
echo 'B|';
try {
    $result = $call->__invoke('V95_REVIEW_DIRECT', $payload, v95ReviewFlag());
    echo 'BAD_RETURN|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $rawApi = $trace[1]['args'];
    $rawInvoke = $trace[2]['args'];
    $raw = $rawApi[1];
    echo 'E|', $error === $chosen ? 'same|' : 'BAD|';
    echo $error->getMessage(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|', $trace[1]['function'], '|', $trace[2]['function'], '|';
    echo $rawApi[0], '|';
    echo $rawApi[2] === false ? 'false|' : 'BAD|';
    echo $rawInvoke === $rawApi ? 'rawsame|' : 'BAD|';
    echo $raw->value, '|', $calls, '|', $destroyed, '|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $call, '|';
    echo $payload === null && $cell === null ? 'null|' : 'BAD|';
    echo $result, '|';
    $raw->value = 53;
    $again = $rawInvoke[1];
    echo $again === $raw ? 'shared|' : 'BAD|';
    echo $again->value, '|';
    unset($again, $trace, $error, $chosen);
    echo 'kept|', $destroyed, '|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    unset($rawInvoke, $rawApi, $raw);
    echo 'released|', $destroyed, '|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
}
restore_error_handler();
echo constant('V95_REVIEW_DIRECT'), '|A|';
unset($weak, $call, $payload, $cell, $calls, $destroyed, $result);
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name == CASE:
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '180']
        timeout = 195
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
