#!/usr/bin/env python3
"""Native-first Stringable query names convert before class-constant lookup."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'stringable-loaded-class-value-and-existence': br'''<?php
class LoadedValueQuery58 { public const VALUE = 1693; }
class StringClassQuery58 {
    public function __toString(): string {
        global $calls; echo 'S|'; $calls++; return 'LoadedValueQuery58::VALUE';
    }
}
$name = new StringClassQuery58; $keep = $name; $calls = 0;
echo 'B|', constant($name), '|', defined($name) ? 'T' : 'BAD', '|', $calls;
''',
    'selected-stringable-class-query-keeps-converted-missing-member': br'''<?php
class MissingValueQuery58 { public const PRESENT = 1709; }
class CapturedClassQuery58 {
    public function __toString(): string {
        global $call, $name, $calls;
        echo 'S|'; $calls++; $call = 'defined'; $name = 'cast-live58';
        $part = 'MissingValueQuery58'; return $part . '::MISSING';
    }
}
function classQueryArgument58() {
    global $call, $name, $effects;
    $earlier = $name; echo 'N|'; $effects++; $call = 'defined';
    $name = 'argument-live58'; return $earlier;
}
function classQueryCaller58() {
    global $call, $name, $calls, $effects;
    $call = 'CoNsTaNt'; $name = new CapturedClassQuery58; $keep = $name;
    $calls = 0; $effects = 0; $result = 99;
    try { $result = $call(classQueryArgument58()); echo 'BAD'; }
    catch (Error $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === 'MissingValueQuery58::MISSING' ? 'N' : 'BAD';
        echo '|', $trace[1]['function'], '|', $result, '|', $calls, '|', $effects;
    }
    echo '|', $call, '|', $name;
}
echo 'B|'; classQueryCaller58();
''',
    'missing-class-member-query-recovers-with-global-stringable-name': br'''<?php
class RecoveryValueQuery58 { public const VALUE = 1717; }
class RecoverClassQuery58 {
    public function __toString(): string {
        global $calls; echo 'S|'; $calls++;
        if ($calls === 1) { return 'RecoveryValueQuery58::ABSENT'; }
        return 'TRUE';
    }
}
$name = new RecoverClassQuery58; $keep = $name; $calls = 0;
echo 'B|', defined($name) === false ? 'F' : 'BAD';
echo '|', constant($name) === true ? 'T' : 'BAD', '|', $calls;
''',
}
family.BASELINE = ('Stringable query global name', b'B|S|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
