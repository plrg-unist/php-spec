#!/usr/bin/env python3
"""Later positional delivery precedes earlier named extras inside Closure::call."""
from pathlib import Path

import global_constant_sources as family

CASE = 'closure-call-named-before-positional-reference-duplicate'
family.CASES = {
    CASE: br'''<?php
declare(strict_types=1);
class V108ReviewReceiver {}
function v108ReviewNamed() {
    global $namedPack, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $saved = $namedPack;
    $namedPack = null;
    echo 'N|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V108ReviewReceiver ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
function v108ReviewPositional() {
    global $call, $receiver, $positionalPack, $namedCell, $positionalCell, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $namedCell = 29;
    $positionalCell = 31;
    $saved = $positionalPack;
    $positionalPack = null;
    $call = null;
    $receiver = null;
    echo 'P|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V108ReviewReceiver ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
function v108ReviewWarning($number, $message, $file, $line) {
    global $namedCell, $positionalCell, $weakCall, $weakReceiver, $warnings;
    ++$warnings;
    echo 'W|', $number, '|', $message, '|';
    echo $file === __FILE__ ? 'warningFile|' : 'otherFile|';
    echo $line, '|', $namedCell, '|', $positionalCell, '|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V108ReviewReceiver ? 'receiverHeld|' : 'receiverGone|';
    $namedCell = 47;
    $positionalCell = 53;
    return true;
}
$namedCell = 17;
$positionalCell = 23;
$namedPack = ['x' => &$namedCell];
$positionalPack = [9 => &$positionalCell];
$receiver = new V108ReviewReceiver;
$bodies = 0;
$call = function (&$x) { global $bodies; ++$bodies; return 99; };
$weakCall = WeakReference::create($call);
$weakReceiver = WeakReference::create($receiver);
$effects = 0;
$warnings = 0;
$result = 97;
$raw = null;
set_error_handler('v108ReviewWarning');
echo 'B|';
try {
    $result = $call->call($receiver, ...v108ReviewNamed(), ...v108ReviewPositional());
    echo 'RETURN|';
} catch (Error $error) {
    $trace = $error->getTrace();
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'chained|';
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
        echo isset($raw[0]) && $raw[0] === $weakReceiver->get() ? 'rawReceiver|' : 'noReceiver|';
        echo isset($raw[1]) && $raw[1] === 31 ? 'pos31|' : 'otherPos|';
        echo isset($raw['x']) && $raw['x'] === 17 ? 'named17|' : 'otherNamed|';
    } else { echo 'noTrace|'; }
    echo isset($trace[1]) ? 'more|' : 'end|';
    echo $namedCell, '|', $positionalCell, '|', $result, '|', $effects, '|', $warnings, '|', $bodies, '|';
    echo $call === null && $receiver === null && $namedPack === null && $positionalPack === null ? 'currentNull|' : 'changed|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakReceiver->get() instanceof V108ReviewReceiver ? 'receiverHeld|' : 'receiverGone|';
    unset($error, $trace, $namedCell, $positionalCell);
    echo isset($raw[1]) && $raw[1] === 31 ? 'posKept|' : 'posChanged|';
    echo isset($raw['x']) && $raw['x'] === 17 ? 'namedKept|' : 'namedChanged|';
    echo $weakReceiver->get() instanceof V108ReviewReceiver ? 'rawHeld|' : 'rawGone|';
    unset($raw);
    echo $weakReceiver->get() === null ? 'released|' : 'held|';
}
restore_error_handler();
$recovery = function () { return 23; };
echo $recovery(), '|';
unset($recovery, $call, $receiver, $namedPack, $positionalPack, $namedCell, $positionalCell, $weakCall, $weakReceiver, $effects, $warnings, $bodies, $result, $raw);
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
