#!/usr/bin/env python3
"""Explicit reception stays weak in a strict caller and cancels before DEFINE."""
from pathlib import Path

import global_constant_sources as family


CASE = 'owned-null-flag-exception-cancels-object-publication'
family.CASES = {
    CASE: br'''<?php
declare(strict_types=1);
class V97ReviewPayload {
    public int $value = 7;
    function __destruct() {
        global $weak;
        echo 'D|', $this->value, '|';
        echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    }
}
function v97ReviewFlag() {
    global $call, $payload, $cell, $weak;
    $cell->value = 31;
    $payload = null;
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return null;
}
function v97ReviewReport($level, $message) {
    global $cell, $calls, $weak, $chosen;
    ++$calls;
    $cell->value = 41;
    $cell = null;
    echo 'H|', $level, '|';
    echo defined('V97_REVIEW_NULL') ? 'BAD_DEFINED|' : 'absent|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    $chosen = new Exception('STOP');
    throw $chosen;
}
$payload = new V97ReviewPayload;
$cell = $payload;
$pointerWeak = WeakReference::create($payload);
$call = define(...);
$weak = WeakReference::create($call);
$calls = 0;
$result = 97;
$chosen = null;
set_error_handler('v97ReviewReport');
echo 'B|';
try {
    $result = $call->__invoke('V97_REVIEW_NULL', $payload, v97ReviewFlag());
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
    echo $rawApi[2] === null ? 'null|' : 'BAD|';
    echo $rawInvoke === $rawApi ? 'rawsame|' : 'BAD|';
    echo $raw->value, '|', $calls, '|', $result, '|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $call, '|';
    echo $payload === null && $cell === null ? 'null|' : 'BAD|';
    echo defined('V97_REVIEW_NULL') ? 'BAD_DEFINED|' : 'absent|';
    $raw->value = 53;
    echo $raw->value, '|kept|';
    unset($rawInvoke, $rawApi, $raw, $trace, $error, $chosen);
    echo 'released|';
    echo $pointerWeak->get() === null ? 'dead|' : 'BAD_ALIVE|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
}
restore_error_handler();
echo defined('V97_REVIEW_NULL') ? 'BAD_DEFINED|' : 'absent|';
echo $calls, '|', $result, '|A|';
unset($call, $weak, $pointerWeak, $payload, $cell, $calls, $result);
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
