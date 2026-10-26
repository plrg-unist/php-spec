#!/usr/bin/env python3
"""Closure::call expands ARRAY packs into saved positional and named arguments."""
from pathlib import Path

import global_constant_sources as family

POSITIONAL = 'closure-call-positional-array-pack-saved-receiver'
NAMED = 'closure-call-named-array-pack-default-and-error'
family.CASES = {
    POSITIONAL: br'''<?php
declare(strict_types=1);
class V107PositionalBox { public int $tag = 17; }
function v107PositionalPack() {
    global $call, $receiver, $pack, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $saved = $pack;
    $pack[4] = '99';
    $call = null;
    $receiver = null;
    echo 'P|';
    echo $weakCall->get() instanceof Closure ? 'callHeld|' : 'callGone|';
    echo $weakReceiver->get() instanceof V107PositionalBox ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
$receiver = new V107PositionalBox;
$weakReceiver = WeakReference::create($receiver);
$bodies = 0;
$call = function (int $first, string $second) {
    global $weakCall, $weakReceiver, $bodies;
    ++$bodies;
    echo 'F|', $this->tag, '|';
    echo $first === 7 ? 'int|' : 'BAD|';
    echo $second === '5' ? 'string|' : 'BAD|';
    echo $weakCall->get() instanceof Closure ? 'callHeld|' : 'callGone|';
    echo $weakReceiver->get() instanceof V107PositionalBox ? 'receiverHeld|' : 'receiverGone|';
    return $first + 10;
};
$weakCall = WeakReference::create($call);
$first = '7';
$second = 5;
$pack = [4 => $first, 9 => $second];
$effects = 0;
$result = 97;
echo 'B|';
try {
    $result = $call->call($receiver, ...v107PositionalPack());
    echo 'R|', $result, '|', $effects, '|', $bodies, '|', $pack[4], '|';
} catch (Throwable $error) {
    echo 'E|', $error->getMessage(), '|', $result, '|';
}
echo $call === null && $receiver === null ? 'currentNull|' : 'BAD|';
echo $weakCall->get() === null ? 'callGone|' : 'callHeld|';
echo $weakReceiver->get() === null ? 'receiverGone|' : 'receiverHeld|';
unset($error, $call, $receiver, $pack, $first, $second, $weakCall, $weakReceiver, $effects, $bodies, $result);
echo 'A|';
''',
    NAMED: br'''<?php
class V107NamedBox { public int $tag = 23; }
function v107NamedPack() {
    global $call, $receiver, $pack, $weakCall, $weakReceiver, $effects, $mode;
    ++$effects;
    $saved = $pack;
    if ($mode === 0) { $pack['second'] = 99; }
    else { $call = null; $receiver = null; $pack = null; }
    echo 'P|';
    echo $weakCall->get() instanceof Closure ? 'callHeld|' : 'callGone|';
    echo $weakReceiver->get() instanceof V107NamedBox ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
$receiver = new V107NamedBox;
$weakReceiver = WeakReference::create($receiver);
$bodies = 0;
$call = function ($first = 17, $second = 19) {
    global $bodies;
    ++$bodies;
    echo 'F|', $this->tag, '|', $first, '|', $second, '|';
    return $first + $second;
};
$weakCall = WeakReference::create($call);
$number = 29;
$pack = ['second' => $number];
$mode = 0;
$effects = 0;
$result = 97;
$raw = null;
echo 'B|';
$result = $call->call($receiver, ...v107NamedPack());
echo 'R|', $result, '|', $effects, '|', $bodies, '|', $pack['second'], '|';
$number = 31;
$pack = ['unknown' => $number];
$mode = 1;
$result = 97;
try {
    $result = $call->call($receiver, ...v107NamedPack());
    echo 'BAD_RETURN|';
} catch (Error $error) {
    $trace = $error->getTrace();
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
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
        if (isset($raw['unknown'])) { echo $raw['unknown'] === 31 ? 'named31|' : 'other|'; }
        elseif (isset($raw[1])) { echo $raw[1] === 31 ? 'indexed31|' : 'other|'; }
        else { echo 'noValue|'; }
    } else { echo 'noTrace|'; }
    echo isset($trace[1]) ? 'more|' : 'end|';
    echo $call === null && $receiver === null && $pack === null ? 'currentNull|' : 'BAD|';
    echo $weakCall->get() === null ? 'callGone|' : 'callHeld|';
    echo $weakReceiver->get() instanceof V107NamedBox ? 'receiverHeld|' : 'receiverGone|';
    echo $result, '|', $effects, '|', $bodies, '|';
}
unset($error, $trace);
echo $weakReceiver->get() instanceof V107NamedBox ? 'rawHeld|' : 'rawGone|';
unset($raw);
echo $weakReceiver->get() === null ? 'released|' : 'held|';
$recovery = function () { return 23; };
echo $recovery(), '|';
unset($recovery, $call, $receiver, $pack, $number, $mode, $weakCall, $weakReceiver, $effects, $bodies, $result);
echo 'A|';
''',
}
family.BASELINE = ('Closure::call argument form', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name in family.CASES:
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
