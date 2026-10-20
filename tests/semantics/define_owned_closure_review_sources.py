#!/usr/bin/env python3
"""Owned DEFINE identity remains live for arguments, never for history alone."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-define-explicit-capture-receipts-and-weak-owner-retirement': br'''<?php
function v93ReviewFlag() {
    global $call, $replacement, $value, $phase, $weakA, $weakB;
    $phase++;
    echo 'N|', $phase, '|';
    if ($phase === 1) {
        $call = $replacement;
        $value = 47;
        echo $weakA->get() instanceof Closure ? 'held|' : 'BAD|';
    } else {
        $call = 'defined';
        $replacement = null;
        $value = 53;
        echo $weakB->get() instanceof Closure ? 'held|' : 'BAD|';
    }
    return false;
}
function v93ReviewReport($level, $message) {
    global $calls, $weakB, $chosen;
    $calls++;
    echo 'H|', $level, '|', constant('V93_REVIEW_OWNED'), '|';
    echo $weakB->get() instanceof Closure ? 'held|' : 'BAD|';
    $chosen = new Exception('STOP');
    throw $chosen;
}
$call = define(...);
$replacement = define(...);
$weakA = WeakReference::create($call);
$weakB = WeakReference::create($replacement);
$phase = 0;
$value = 23;
$calls = 0;
echo 'B|';
$result = $call->__invoke('V93_REVIEW_OWNED', $value, v93ReviewFlag());
echo $result === true ? 'T|' : 'BAD|';
echo $call === $replacement ? 'same|' : 'BAD|';
echo $weakA->get() === null ? 'gone|' : 'BAD|';
echo constant('V93_REVIEW_OWNED'), '|', $value, '|';
$value = 31;
$result = 97;
$chosen = null;
set_error_handler('v93ReviewReport');
try {
    $result = $call->__invoke('V93_REVIEW_OWNED', $value, v93ReviewFlag());
    echo 'BAD_RETURN|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $rawApi = $trace[1]['args'];
    $rawInvoke = $trace[2]['args'];
    echo 'E|', $error === $chosen ? 'same|' : 'BAD|';
    echo $error->getMessage(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|', $trace[1]['function'], '|', $trace[2]['function'], '|';
    echo $rawApi[0], '|', $rawApi[1], '|';
    echo $rawApi[2] === false ? 'false|' : 'BAD|';
    echo $rawInvoke === $rawApi ? 'rawsame|' : 'BAD|';
    echo $call, '|', $value, '|', $result, '|', $calls, '|';
    unset($rawInvoke, $rawApi, $trace, $error, $chosen);
}
restore_error_handler();
echo $weakA->get() === null ? 'gone|' : 'BAD|';
echo $weakB->get() === null ? 'gone|' : 'BAD|';
echo constant('V93_REVIEW_OWNED'), '|';
echo $call('V93_REVIEW_OWNED') ? 'legacy|' : 'BAD|';
echo 'A|';
unset($weakA, $weakB, $call, $replacement, $value, $phase, $calls, $result);
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and Path(stem).parent.name ==
            'owned-define-explicit-capture-receipts-and-weak-owner-retirement'):
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
