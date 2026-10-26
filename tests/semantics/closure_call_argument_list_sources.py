#!/usr/bin/env python3
"""Closure::call collects complete ARRAY-pack lists before inner forwarding."""
from pathlib import Path

import global_constant_sources as family

NORMAL = 'closure-call-list-canonical-order-and-mixed-delivery'
OUTER = 'closure-call-list-outer-rejection-stops-producers'
family.CASES = {
    NORMAL: br'''<?php
declare(strict_types=1);
class V108Box { public int $tag = 17; }
function v108NamedPack() {
    global $call, $namedPack, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $saved = $namedPack;
    $namedPack['third'] = 99;
    $call = null;
    echo 'N|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V108Box ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
function v108PositionalPack() {
    global $receiver, $positionalPack, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $saved = $positionalPack;
    $positionalPack = null;
    $receiver = null;
    echo 'P|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V108Box ? 'receiverHeld|' : 'receiverGone|';
    return $saved;
}
function v108MixedPack() {
    global $mixedPack, $direct, $effects;
    ++$effects;
    $direct = '99';
    $saved = $mixedPack;
    $mixedPack[4] = 99;
    echo 'M|';
    return $saved;
}
function v108NamedTail() {
    global $call, $receiver, $mixedPack, $weakCall, $weakReceiver, $effects;
    ++$effects;
    $call = null;
    $receiver = null;
    $mixedPack = null;
    echo 'T|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    echo $weakReceiver->get() instanceof V108Box ? 'receiverHeld|' : 'receiverGone|';
    return 47;
}
$receiver = new V108Box;
$weakReceiver = WeakReference::create($receiver);
$call = function (int $first = 11, string $second = '13', int $third = 19) {
    global $bodies;
    ++$bodies;
    echo 'BODY|', $this->tag, '|', $first, '|', $second, '|', $third, '|';
    echo $first === 7 && $second === '13' ? 'received|' : 'BAD|';
    return $first + $third;
};
$weakCall = WeakReference::create($call);
$number = 29;
$value = '7';
$namedPack = ['third' => $number];
$positionalPack = [9 => $value];
$effects = 0;
$bodies = 0;
$result = 97;
echo 'B|';
$result = $call->call($receiver, ...v108NamedPack(), ...v108PositionalPack());
echo 'R|', $result, '|', $effects, '|', $bodies, '|', $namedPack['third'], '|';
echo $call === null && $receiver === null && $positionalPack === null ? 'currentNull|' : 'BAD|';
echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $weakReceiver->get() === null ? 'receiverGone|' : 'receiverHeld|';
$receiver = new V108Box;
$weakReceiver = WeakReference::create($receiver);
$call = function (int $first, int $second = 13, ...$rest) {
    global $bodies;
    ++$bodies;
    echo 'BODY2|', $this->tag, '|', $first, '|', $second, '|', $rest[0], '|', $rest['third'], '|', $rest['fourth'], '|';
    return $first + $second + $rest[0] + $rest['third'] + $rest['fourth'];
};
$weakCall = WeakReference::create($call);
$direct = '5';
$number = 17;
$extra = 23;
$named = 29;
$mixedPack = [4 => $number, 9 => $extra, 'third' => $named];
$effects = 0;
$bodies = 0;
$result = 97;
$result = $call->call($receiver, $direct, ...v108MixedPack(), fourth: v108NamedTail());
echo 'R2|', $result, '|', $effects, '|', $bodies, '|', $direct, '|';
echo $call === null && $receiver === null && $mixedPack === null ? 'currentNull|' : 'BAD|';
echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $weakReceiver->get() === null ? 'receiverGone|' : 'receiverHeld|';
$recover = static function () { return 23; };
echo $recover(), '|';
unset($call, $receiver, $namedPack, $positionalPack, $mixedPack, $weakCall, $weakReceiver, $number, $value, $direct, $extra, $named, $effects, $bodies, $result, $recover);
echo 'A|';
''',
    OUTER: br'''<?php
class V108OuterBox {}
function v108OuterPack($which) {
    global $call, $receiver, $left, $right, $effects;
    ++$effects;
    if ($which === 0) {
        echo 'L|';
        return $left;
    }
    $saved = $right;
    $left = null;
    $right = null;
    $call = null;
    $receiver = null;
    echo 'R|';
    return $saved;
}
function v108OuterTail() {
    global $call, $receiver, $left, $effects;
    ++$effects;
    $call = null;
    $receiver = null;
    $left = null;
    echo 'T|';
    return 29;
}
function v108OuterNever() {
    global $skipped;
    ++$skipped;
    echo 'BAD_LATE|';
    return ['later' => 41];
}
function v108OuterReport($error) {
    global $weakCall, $weakReceiver, $effects, $bodies, $result, $skipped;
    $trace = $error->getTrace();
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getFile() === __FILE__ ? 'file|' : 'otherFile|';
    echo $error->getPrevious() === null ? 'none|' : 'previous|';
    echo isset($trace[0]) ? 'frame|' : 'noFrame|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakReceiver->get() === null ? 'receiverGone|' : 'receiverHeld|';
    echo $result, '|', $effects, '|', $bodies, '|', $skipped, '|';
}
$effects = 0;
$bodies = 0;
$skipped = 0;
$result = 97;
$number = 17;
$other = 29;
$receiver = new V108OuterBox;
$weakReceiver = WeakReference::create($receiver);
$call = function ($x = 11) { global $bodies; ++$bodies; return $x; };
$weakCall = WeakReference::create($call);
$left = ['x' => $number];
$right = ['x' => $other];
echo 'B|';
try { $result = $call->call($receiver, ...v108OuterPack(0), ...v108OuterPack(1), ...v108OuterNever()); }
catch (Error $error) { v108OuterReport($error); }
unset($error);
$receiver = new V108OuterBox;
$weakReceiver = WeakReference::create($receiver);
$call = function ($x = 11) { global $bodies; ++$bodies; return $x; };
$weakCall = WeakReference::create($call);
$right = ['x' => $number, 9 => $other];
try { $result = $call->call($receiver, ...v108OuterPack(1), ...v108OuterNever()); }
catch (Error $error) { v108OuterReport($error); }
unset($error);
$receiver = new V108OuterBox;
$weakReceiver = WeakReference::create($receiver);
$call = function ($x = 11) { global $bodies; ++$bodies; return $x; };
$weakCall = WeakReference::create($call);
$left = ['x' => $number];
try { $result = $call->call($receiver, ...v108OuterPack(0), x: v108OuterTail(), later: v108OuterNever()); }
catch (Error $error) { v108OuterReport($error); }
unset($error);
$recover = static function () { return 23; };
echo $recover(), '|';
unset($call, $receiver, $left, $right, $weakCall, $weakReceiver, $number, $other, $effects, $bodies, $skipped, $result, $recover);
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
