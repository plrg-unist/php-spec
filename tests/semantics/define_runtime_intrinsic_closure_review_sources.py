#!/usr/bin/env python3
"""Distinct DEFINE callees and raw Closure values retain their own identities."""
from pathlib import Path

import global_constant_sources as family


CASE = 'intrinsic-value-trace-recovery-and-selected-writer'
family.CASES = {
    CASE: br'''<?php
function v98ReviewFlag() {
    global $call, $value, $weakA, $weakB;
    $call = 'defined';
    $value = null;
    echo 'N|';
    echo $weakA->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    echo $weakB->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return false;
}
function v98ReviewRecoveryFlag() {
    global $call, $weakB;
    $call = 'constant';
    echo 'R|';
    echo $weakB->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return false;
}
function v98ReviewReport($level, $message) {
    global $calls, $chosen, $weakA, $weakB;
    ++$calls;
    echo 'H|', $level, '|';
    echo $weakA->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    echo $weakB->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    echo constant('V98_REVIEW_OLD'), '|';
    $chosen = new Exception('STOP');
    throw $chosen;
}
define('V98_REVIEW_OLD', 17);
$call = define(...);
$value = define(...);
$weakA = WeakReference::create($call);
$weakB = WeakReference::create($value);
$calls = 0;
$result = 97;
$chosen = null;
set_error_handler('v98ReviewReport');
echo 'B|';
echo $call !== $value ? 'distinct|' : 'BAD_SAME|';
try {
    $result = $call->__invoke('V98_REVIEW_OLD', $value, v98ReviewFlag());
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
    echo $weakA->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $weakB->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    echo $raw === $weakB->get() ? 'same-value|' : 'BAD|';
    echo $call, '|';
    echo $value === null ? 'null|' : 'BAD|';
    echo $result, '|', constant('V98_REVIEW_OLD'), '|';
    $call = $raw;
    $recovery = $call('V98_REVIEW_NEW', 23, v98ReviewRecoveryFlag());
    echo $recovery === true ? 'T|' : 'BAD|';
    echo $weakB->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    echo $call, '|', constant('V98_REVIEW_NEW'), '|';
    unset($raw, $rawApi, $rawInvoke, $trace, $error, $chosen);
    echo $weakA->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $weakB->get() === null ? 'gone|' : 'BAD_HELD|';
}
restore_error_handler();
echo 'Q|', constant('V98_REVIEW_OLD'), '|', constant('V98_REVIEW_NEW'), '|';
echo $calls, '|', $result, '|A|';
unset($call, $value, $weakA, $weakB, $calls, $result, $recovery);
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
