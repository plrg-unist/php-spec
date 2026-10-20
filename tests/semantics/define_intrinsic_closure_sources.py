#!/usr/bin/env python3
"""Bare intrinsic Closure values keep identity through rows, COW and owner calls."""
from pathlib import Path

import global_constant_sources as family

DIRECT = 'intrinsic-closure-value-and-query-derived-writer'
family.CASES = {
    DIRECT: br'''<?php
function v98Name() {
    global $call, $value, $other, $left, $weak;
    $value = $other;
    $left = null;
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return 'V98_DEFINE';
}
function v98WriterName() {
    global $writer;
    $writer = 'defined';
    echo 'W|';
    return 'V98_RESULT';
}
$left = define(...);
$other = define(...);
$pointer = WeakReference::create($left);
$value = $left;
$call = define(...);
$weak = WeakReference::create($call);
echo 'B|';
$result = $call(value: $value, constant_name: v98Name());
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
$stored = constant('V98_DEFINE');
echo $stored === $pointer->get() ? 'same|' : 'BAD|';
echo $stored !== $value ? 'split|' : 'BAD|';
echo $left === null ? 'null|' : 'BAD|';
echo $call, '|';
unset($value, $other, $left, $call, $weak);
$writer = $stored;
unset($stored);
$result = $writer(value: 23, constant_name: v98WriterName());
echo $result === true ? 'T|' : 'BAD|';
echo $writer, '|', constant('V98_RESULT'), '|';
echo $pointer->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
unset($writer, $result);
$again = constant('V98_DEFINE');
echo $again === $pointer->get() ? 'same|' : 'BAD|';
echo 'A|';
unset($again, $pointer);
''',
    'intrinsic-closure-array-copy-and-query-cow': br'''<?php
function v98ArrayName() {
    global $call, $input, $cell, $replacement, $weak;
    $cell = $replacement;
    $replacement = null;
    $input = [90 => 31];
    $call = 'defined';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return 'V98_ARRAY';
}
$old = define(...);
$replacement = define(...);
$has = defined(...);
$read = constant(...);
$oldWeak = WeakReference::create($old);
$pointer = WeakReference::create($replacement);
$hasWeak = WeakReference::create($has);
$readWeak = WeakReference::create($read);
$cell = $old;
$input = [90 => 0, 'write' => &$cell, 'has' => $has, 'read' => $read];
unset($input[90], $old);
$raw = $input;
$call = define(...);
$weak = WeakReference::create($call);
echo 'B|';
$result = $call(value: $input, constant_name: v98ArrayName());
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
echo $oldWeak->get() === null ? 'old-gone|' : 'BAD_OLD|';
echo $call, '|', $input[90], '|';
$stored = constant('V98_ARRAY');
echo $stored['write'] === $pointer->get() ? 'same|' : 'BAD|';
echo $stored['has'] === $has ? 'has|' : 'BAD|';
echo $stored['read'] === $read ? 'read|' : 'BAD|';
$cell = null;
unset($has, $read, $replacement);
$stored['write'] = null;
$stored[] = 'local';
$raw[] = 'raw';
$again = constant('V98_ARRAY');
echo $stored['write'] === null ? 'local-null|' : 'BAD|';
echo $again['write'] === $pointer->get() ? 'same|' : 'BAD|';
echo $again['has'] === $hasWeak->get() && $again['read'] === $readWeak->get() ? 'identities|' : 'BAD|';
echo isset($raw[91]) && !isset($raw[0]) && isset($stored[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
$writer = $again['write'];
$result = $writer('V98_ARRAY_RESULT', 17);
echo $result === true ? 'T|' : 'BAD|';
unset($writer, $again, $stored, $raw, $input, $cell, $call, $weak, $result);
echo constant('V98_ARRAY_RESULT'), '|';
echo $pointer->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
echo 'A|';
unset($oldWeak, $pointer, $hasWeak, $readWeak);
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|N|held|')
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
