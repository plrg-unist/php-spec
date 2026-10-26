#!/usr/bin/env python3
"""Closure::call copies ARRAY aliases before isolated reference forwarding."""
from pathlib import Path

import global_constant_sources as family

CASE = 'closure-call-array-pack-alias-detached-reference'
family.CASES = {
    CASE: br'''<?php
declare(strict_types=1);
class V107ReviewReceiver {}
function v107ReviewPack() {
    global $call, $receiver, $pack, $cell, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $cell = 31;
    $saved = $pack;
    $pack = null;
    $receiver = null;
    $call = static function ($value) { return $value; };
    echo 'P|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V107ReviewReceiver ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
function v107ReviewWarning($number, $message, $file, $line) {
    global $cell, $noise, $noiseAlias, $weakCall, $weakReceiver, $warnings;
    ++$warnings;
    echo 'W|', $number, '|', $message, '|';
    echo $file === __FILE__ ? 'warningFile|' : 'otherFile|';
    echo $line, '|', $cell, '|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V107ReviewReceiver ? 'receiverHeld|' : 'receiverGone|';
    $cell = 47;
    $noise = 71;
    $noiseAlias =& $noise;
    return true;
}
$cell = 17;
$pack = ['value' => &$cell];
$receiver = new V107ReviewReceiver;
$call = function (&$value) {
    global $cell, $bodyCount, $weakCall, $weakReceiver;
    ++$bodyCount;
    echo 'BODY|', $value, '|', $cell, '|';
    echo $this instanceof V107ReviewReceiver ? 'bound|' : 'unbound|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V107ReviewReceiver ? 'receiverHeld|' : 'receiverGone|';
    $value = 53;
    echo $cell, '|';
    return $value;
};
$weakCall = WeakReference::create($call);
$weakReceiver = WeakReference::create($receiver);
$effects = 0;
$warnings = 0;
$bodyCount = 0;
$result = 97;
set_error_handler('v107ReviewWarning');
echo 'B|';
$result = $call->call($receiver, ...v107ReviewPack());
restore_error_handler();
echo $result, '|', $cell, '|', $effects, '|', $warnings, '|', $bodyCount, '|';
echo $pack === null && $receiver === null ? 'currentNull|' : 'changed|';
echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $weakReceiver->get() === null ? 'receiverGone|' : 'receiverHeld|';
echo $noiseAlias, '|', $call(23), '|';
unset($call, $receiver, $pack, $cell, $noise, $noiseAlias, $weakCall, $weakReceiver, $effects, $warnings, $bodyCount, $result);
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
