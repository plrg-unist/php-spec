#!/usr/bin/env python3
"""Captured query APIs retain their owner, spelling and selected constant value."""
from pathlib import Path

import global_constant_sources as family

DIRECT = 'owned-query-named-capture-and-late-definition'
family.CASES = {
    DIRECT: br'''<?php
function v99HasName(&$call, &$other, &$name, $weak) {
    $saved = $name;
    $call = $other;
    $other = null;
    $name = 'V99_MISSING';
    define('V99_LATE', 17);
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
function v99ReadName(&$call, &$name, $weak) {
    $saved = $name;
    $call = 'defined';
    $name = 'V99_MISSING';
    echo 'R|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
$call = defined(...);
$other = constant(...);
$weak = WeakReference::create($call);
$weakRead = WeakReference::create($other);
$name = '\\V99_LATE';
$result = 97;
echo 'B|';
$result = $call(constant_name: v99HasName($call, $other, $name, $weak));
echo $result === true ? 'T|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
echo $other === null ? 'null|' : 'BAD|';
echo $name, '|', constant('V99_LATE'), '|';
$name = '\\V99_LATE';
$result = $call(name: v99ReadName($call, $name, $weakRead));
echo $result, '|';
echo $weakRead->get() === null ? 'gone|' : 'BAD_HELD|';
echo $call, '|', $name, '|';
echo $call($name) === false ? 'F|' : 'BAD|';
unset($call, $other, $name, $weak, $weakRead, $result);
echo 'A|';
''',
    'owned-query-derived-reader-array-cow': br'''<?php
function v99ArrayName(&$call, &$name, &$input, &$cell, $weak) {
    $saved = $name;
    $cell = 23;
    $input = [90 => 31];
    $call = 'defined';
    $name = 'V99_MISSING';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
$reader = constant(...);
define('V99_READER', $reader);
unset($reader);
$call = constant('V99_READER');
$weak = WeakReference::create($call);
$cell = 17;
$input = [90 => 0, 'leaf' => &$cell];
unset($input[90]);
$raw = $input;
define('V99_TREE', $input);
$name = '\\V99_TREE';
echo 'B|';
$local = $call->__invoke(name: v99ArrayName($call, $name, $input, $cell, $weak));
echo $local['leaf'], '|', $cell, '|', $input[90], '|', $call, '|', $name, '|';
$local['leaf'] = 41;
$local[] = 5;
$raw[] = 7;
$again = constant('V99_TREE');
echo $again['leaf'], '|', $local['leaf'], '|';
echo isset($local[0]) && isset($raw[91]) ? 'history|' : 'BAD|';
$reader = constant('V99_READER');
echo $reader === $weak->get() ? 'same|' : 'BAD|';
unset($reader, $again, $local, $raw, $input, $cell, $call, $name);
echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
unset($weak);
echo 'A|';
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
