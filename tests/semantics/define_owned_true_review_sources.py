#!/usr/bin/env python3
"""An ignored-flag Exception preserves a fresh owned direct-object publication."""
from pathlib import Path

import global_constant_sources as family


CASE = 'owned-true-pending-exception-registers-direct-object'
family.CASES = {
    CASE: br'''<?php
class V96ReviewPayload {
    public int $value = 7;
    function __destruct() {
        echo 'D|', $this->value, '|';
    }
}
function v96ReviewFlag() {
    global $call, $payload, $cell, $weak;
    $cell->value = 31;
    $payload = null;
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return true;
}
function v96ReviewReport($level, $message) {
    global $cell, $calls, $weak, $chosen;
    ++$calls;
    $cell->value = 41;
    $cell = null;
    echo 'H|', $level, '|';
    echo defined('V96_REVIEW_TRUE') ? 'BAD_DEFINED|' : 'absent|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    $chosen = new Exception('STOP');
    throw $chosen;
}
$payload = new V96ReviewPayload;
$cell = $payload;
$pointerWeak = WeakReference::create($payload);
$call = define(...);
$weak = WeakReference::create($call);
$calls = 0;
$result = 97;
$chosen = null;
set_error_handler('v96ReviewReport');
echo 'B|';
try {
    $result = $call->__invoke('V96_REVIEW_TRUE', $payload, v96ReviewFlag());
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
    echo $rawApi[2] === true ? 'true|' : 'BAD|';
    echo $rawInvoke === $rawApi ? 'rawsame|' : 'BAD|';
    echo $raw->value, '|', $calls, '|', $result, '|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $call, '|';
    echo $payload === null && $cell === null ? 'null|' : 'BAD|';
    echo defined('V96_REVIEW_TRUE') ? 'defined|' : 'BAD_MISSING|';
    $published = constant('V96_REVIEW_TRUE');
    echo $published === $raw ? 'same|' : 'BAD|';
    $raw->value = 53;
    echo $published->value, '|';
    unset($published, $rawInvoke, $rawApi, $raw, $trace, $error, $chosen);
    echo 'kept|';
    echo $pointerWeak->get() instanceof V96ReviewPayload ? 'alive|' : 'BAD_DEAD|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
}
restore_error_handler();
$stored = constant('V96_REVIEW_TRUE');
echo 'Q|', $stored->value, '|';
echo $pointerWeak->get() === $stored ? 'same|' : 'BAD|';
echo $calls, '|', $result, '|A|';
unset($stored, $call, $weak, $pointerWeak, $payload, $cell, $calls, $result);
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
