#!/usr/bin/env python3
"""Saved packed newThis wins over live cells and deferred inner-name errors."""
from pathlib import Path

import global_constant_sources as family

CASE = 'closure-call-packed-invalid-receiver-before-inner-duplicate'
family.CASES = {
    CASE: br'''<?php
declare(strict_types=1);
class V109ReviewPayload { public int $tag = 41; }
function v109ReviewNamed() {
    global $namedPack, $payload, $weakCall, $weakPayload, $effects;
    ++$effects;
    $saved = $namedPack;
    $namedPack = null;
    $payload = null;
    echo 'N|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakPayload->get() instanceof V109ReviewPayload ? 'payloadHeld|' : 'payloadGone|';
    return $saved;
}
function v109ReviewReceiver() {
    global $receiverPack, $receiverCell, $effects;
    ++$effects;
    $saved = $receiverPack;
    $receiverPack = null;
    echo 'I|', $receiverCell, '|';
    return $saved;
}
function v109ReviewLater() {
    global $call, $values, $receiverCell, $namedCell, $weakCall, $weakPayload, $effects;
    ++$effects;
    $receiverCell = new V109ReviewPayload;
    $receiverCell->tag = 53;
    $namedCell = $receiverCell;
    $saved = $values;
    $values = null;
    $call = null;
    echo 'L|';
    echo $receiverCell instanceof V109ReviewPayload ? 'currentObject|' : 'currentScalar|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakPayload->get() instanceof V109ReviewPayload ? 'payloadHeld|' : 'payloadGone|';
    return $saved;
}
function v109ReviewWarning($number, $message, $file, $line) {
    global $warnings;
    ++$warnings;
    echo 'BAD_WARNING|', $number, '|', $message, '|';
    return true;
}
$payload = new V109ReviewPayload;
$weakPayload = WeakReference::create($payload);
$namedCell = $payload;
$receiverCell = 17;
$namedPack = ['x' => &$namedCell];
$receiverPack = ['newThis' => &$receiverCell];
$value = 31;
$values = [9 => $value];
$bodies = 0;
$call = function (&$x) { global $bodies; ++$bodies; return 99; };
$weakCall = WeakReference::create($call);
$effects = 0;
$warnings = 0;
$result = 97;
$raw = null;
set_error_handler('v109ReviewWarning');
echo 'B|';
try {
    $result = $call->call(...v109ReviewNamed(), ...v109ReviewReceiver(), ...v109ReviewLater());
    echo 'BAD_RETURN|';
} catch (Throwable $error) {
    $trace = $error->getTrace();
    echo $error instanceof TypeError ? 'TYPE|' : 'OTHER|';
    echo $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'previous|';
    if (isset($trace[0]['args'])) {
        $raw = $trace[0]['args'];
        echo $trace[0]['function'], '|';
        echo isset($trace[0]['class']) ? $trace[0]['class'] : 'noClass';
        echo '|';
        echo isset($trace[0]['type']) ? $trace[0]['type'] : 'noType';
        echo '|';
        echo isset($trace[0]['file']) && $trace[0]['file'] === __FILE__ ? 'file|' : 'noFile|';
        echo isset($trace[0]['line']) ? $trace[0]['line'] : 'internal';
        echo '|';
        echo isset($raw[0]) && $raw[0] === 17 ? 'saved17|' : 'otherReceiver|';
        echo isset($raw[1]) && $raw[1] === 31 ? 'pos31|' : 'otherPos|';
        echo isset($raw['x']) && $raw['x'] === $weakPayload->get() ? 'rawPayload|' : 'otherNamed|';
    } else { echo 'noFrame|'; }
    echo isset($trace[1]) ? 'more|' : 'end|';
    echo $receiverCell instanceof V109ReviewPayload ? 'liveObject|' : 'liveScalar|';
    echo $namedCell->tag, '|', $result, '|', $effects, '|', $warnings, '|', $bodies, '|';
    echo $call === null && $namedPack === null && $receiverPack === null && $values === null ? 'currentNull|' : 'changed|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakPayload->get() instanceof V109ReviewPayload ? 'payloadHeld|' : 'payloadGone|';
    unset($error, $trace, $receiverCell, $namedCell);
    echo isset($raw['x']) && $raw['x'] === $weakPayload->get() ? 'rawKept|' : 'rawChanged|';
    echo $weakPayload->get() instanceof V109ReviewPayload ? 'rawHeld|' : 'rawGone|';
    unset($raw);
    echo $weakPayload->get() === null ? 'released|' : 'held|';
}
restore_error_handler();
$recovery = function () { return 23; };
echo $recovery(), '|';
unset($recovery, $call, $payload, $namedCell, $receiverCell, $namedPack, $receiverPack, $values, $value, $weakCall, $weakPayload, $effects, $warnings, $bodies, $result, $raw);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).parent.name == CASE and Path(stem).name == 'model':
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
