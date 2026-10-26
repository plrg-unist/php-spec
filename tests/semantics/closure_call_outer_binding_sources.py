#!/usr/bin/env python3
"""Closure::call discovers its fixed receiver while collecting ARRAY arguments."""
from pathlib import Path

import global_constant_sources as family

NORMAL = 'closure-call-packed-positional-and-named-receiver'
PRIORITY = 'closure-call-late-receiver-missing-and-duplicate-priority'
family.CASES = {
    NORMAL: br'''<?php
declare(strict_types=1);
class V109Box { public int $tag = 17; }
function v109Extras() {
    global $call, $extras, $weakCall, $effects;
    ++$effects;
    $saved = $extras;
    $extras['second'] = 99;
    $call = null;
    echo 'E|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    return $saved;
}
function v109PositionalReceiver() {
    global $receiver, $positionals, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $saved = $positionals;
    $positionals = null;
    $receiver = null;
    echo 'P|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V109Box ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
function v109NamedReceiver() {
    global $call, $receiver, $named, $other, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $saved = $named;
    $named['newThis'] = $other;
    $named['second'] = 99;
    $call = null;
    $receiver = null;
    echo 'N|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V109Box ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
function v109ValuePack() {
    global $values, $effects;
    ++$effects;
    $saved = $values;
    $values = null;
    echo 'V|';
    return $saved;
}
$receiver = new V109Box;
$weakReceiver = WeakReference::create($receiver);
$call = function (int $first = 11, int $second = 19) {
    global $bodies;
    ++$bodies;
    echo 'BODY|', $this->tag, '|', $first, '|', $second, '|';
    echo $first === 7 ? 'received|' : 'BAD|';
    return $first + $second;
};
$weakCall = WeakReference::create($call);
$number = 29;
$value = '7';
$extras = ['second' => $number];
$positionals = [9 => $receiver, 13 => $value];
$effects = 0;
$bodies = 0;
$result = 97;
echo 'B|';
try {
    $result = $call->call(...v109Extras(), ...v109PositionalReceiver());
    echo 'R|', $result, '|', $effects, '|', $bodies, '|', $extras['second'], '|';
} catch (Throwable $error) { echo 'ERROR|', $error->getMessage(), '|'; }
echo $call === null && $receiver === null && $positionals === null ? 'currentNull|' : 'BAD|';
echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $weakReceiver->get() === null ? 'receiverGone|' : 'receiverHeld|';
$receiver = new V109Box;
$weakReceiver = WeakReference::create($receiver);
$other = new V109Box;
$other->tag = 99;
$call = function (int $first = 11, int $second = 19) {
    global $bodies;
    ++$bodies;
    echo 'BODY2|', $this->tag, '|', $first, '|', $second, '|';
    return $first + $second;
};
$weakCall = WeakReference::create($call);
$named = ['newThis' => $receiver, 'second' => $number];
$values = [21 => $value];
$effects = 0;
$bodies = 0;
$result = 97;
try {
    $result = $call->call(...v109NamedReceiver(), ...v109ValuePack());
    echo 'R2|', $result, '|', $effects, '|', $bodies, '|', $named['second'], '|';
    echo $named['newThis'] === $other ? 'replacement|' : 'BAD|';
} catch (Throwable $error) { echo 'ERROR2|', $error->getMessage(), '|'; }
echo $call === null && $receiver === null && $values === null ? 'currentNull|' : 'BAD|';
echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $weakReceiver->get() === null ? 'receiverGone|' : 'receiverHeld|';
unset($error, $call, $receiver, $extras, $positionals, $named, $values, $other, $weakCall, $weakReceiver, $number, $value, $effects, $bodies, $result);
echo 'A|';
''',
    PRIORITY: br'''<?php
declare(strict_types=1);
class V109PriorityBox { public int $tag = 23; }
function v109Arguments() {
    global $call, $params, $effects;
    ++$effects;
    $saved = $params;
    $params = null;
    $call = null;
    echo 'P|';
    return $saved;
}
function v109LateReceiver() {
    global $receiver, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $saved = $receiver;
    $receiver = null;
    echo 'L|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V109PriorityBox ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
function v109DuplicateReceiver() {
    global $receiver, $effects;
    ++$effects;
    $receiver = null;
    echo 'D|';
    return null;
}
function v109Never() {
    global $skipped;
    ++$skipped;
    echo 'BAD_LATE|';
    return 41;
}
function v109Report($error) {
    global $weakCall, $weakReceiver, $effects, $bodies, $skipped, $result;
    $trace = $error->getTrace();
    echo $error instanceof ArgumentCountError ? 'COUNT|' : 'ERROR|';
    echo $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'previous|';
    if (isset($trace[0]['args'])) {
        $raw = $trace[0]['args'];
        echo $trace[0]['function'], '|';
        echo isset($raw[0]) ? 'slot0|' : 'noSlot0|';
        echo isset($raw['x']) && $raw['x'] === 17 ? 'named17|' : 'noNamed|';
    } else { echo 'noFrame|'; }
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakReceiver->get() === null ? 'receiverGone|' : 'receiverHeld|';
    echo $result, '|', $effects, '|', $bodies, '|', $skipped, '|';
}
$receiver = new V109PriorityBox;
$weakReceiver = WeakReference::create($receiver);
$call = function (int $first = 11, int $second = 19) {
    global $bodies;
    ++$bodies;
    echo 'BODY|', $this->tag, '|', $first, '|', $second, '|';
    return $first + $second;
};
$weakCall = WeakReference::create($call);
$number = 29;
$params = ['second' => $number];
$effects = 0;
$bodies = 0;
$skipped = 0;
$result = 97;
echo 'B|';
try {
    $result = $call->call(...v109Arguments(), newThis: v109LateReceiver());
    echo 'R|', $result, '|', $effects, '|', $bodies, '|';
} catch (Throwable $error) { v109Report($error); }
echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $weakReceiver->get() === null ? 'receiverGone|' : 'receiverHeld|';
unset($error);
$call = function ($x = 11) { global $bodies; ++$bodies; return $x; };
$weakCall = WeakReference::create($call);
$number = 17;
$params = ['x' => $number];
$effects = 0;
$bodies = 0;
$result = 97;
try { $result = $call->call(...v109Arguments()); echo 'BAD_MISSING_RETURN|'; }
catch (Throwable $error) { v109Report($error); }
unset($error);
$receiver = new V109PriorityBox;
$weakReceiver = WeakReference::create($receiver);
$call = function ($x = 11) { global $bodies; ++$bodies; return $x; };
$weakCall = WeakReference::create($call);
$params = ['newThis' => $receiver];
$effects = 0;
$bodies = 0;
$result = 97;
try { $result = $call->call(...v109Arguments(), newThis: v109DuplicateReceiver(), later: v109Never()); echo 'BAD_DUPLICATE_RETURN|'; }
catch (Throwable $error) { v109Report($error); }
unset($error);
$recovery = static function () { return 23; };
echo $recovery(), '|';
unset($recovery, $call, $receiver, $params, $weakCall, $weakReceiver, $number, $effects, $bodies, $skipped, $result);
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
