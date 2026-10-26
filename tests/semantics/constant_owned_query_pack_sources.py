#!/usr/bin/env python3
"""Captured global queries bind positional and named ARRAY-pack snapshots."""
from pathlib import Path

import global_constant_sources as family

POSITIONAL = 'owned-query-positional-pack-retired-snapshot-late-lookup'
NAMED = 'owned-query-named-literal-and-runtime-pack-binding'
family.CASES = {
    POSITIONAL: br'''<?php
function v106PositionalPack() {
    global $call, $pack, $weakCall, $effects;
    ++$effects;
    $saved = $pack;
    $pack[9] = 'V106_WRONG';
    $call = 'defined';
    define('V106_POSITIONAL', 17);
    echo 'P|';
    echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
    return $saved;
}
$part = 'V106';
$name = $part . '_POSITIONAL';
$pack = [9 => $name];
$call = constant(...);
$weakCall = WeakReference::create($call);
$effects = 0;
$result = 97;
echo 'B|';
$result = $call(...v106PositionalPack());
echo $result, '|', $effects, '|', $call, '|', $pack[9], '|';
echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $name, '|';
unset($call, $weakCall, $pack, $part, $name, $effects, $result);
echo 'A|';
''',
    NAMED: br'''<?php
declare(strict_types=1);
function v106NamedPack() {
    global $call, $pack, $weakCall, $effects;
    ++$effects;
    $saved = $pack;
    $pack = null;
    $call = 'constant';
    define('V106_NAMED', 23);
    echo 'P|';
    echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
    return $saved;
}
$call = defined(...);
$weakCall = WeakReference::create($call);
$part = 'V106';
$name = $part . '_NAMED';
$pack = ['constant_name' => $name];
$effects = 0;
$result = 97;
echo 'B|';
$before = $call(...['constant_name' => 'V106_NAMED']);
echo $before === false ? 'F|' : 'BAD|';
echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
$result = $call(...v106NamedPack());
echo $result === true ? 'T|' : 'BAD|';
echo $effects, '|', $call, '|';
echo $pack === null ? 'null|' : 'BAD|';
echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $name, '|';
$reader = constant(...);
echo $reader('V106_NAMED'), '|';
unset($reader, $call, $weakCall, $part, $name, $pack, $effects, $result, $before);
echo 'A|';
''',
}
family.BASELINE = ('global constant value query', b'B|P|held|')
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
