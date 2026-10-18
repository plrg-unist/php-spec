#!/usr/bin/env python3
"""Native-first constant()/defined() count errors before parameter reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'zero-argument-query-errors-retain-caller-result': br'''<?php
$result = 99;
echo 'B|';
try { $result = defined(); echo 'BAD'; }
catch (ArgumentCountError $e) { echo $e->getMessage(), '|', $e->getLine(); }
try { $result = constant(); echo 'BAD'; }
catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'] === [] ? 'E' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $result;
''',
    'selected-constant-extra-arguments-run-before-null-reception': br'''<?php
function constantArityFirst48() { global $call; echo 'A|'; $call = 'defined'; return null; }
function constantArityExtra48() {
    global $call, $effects, $extra;
    echo 'E|'; $effects++; $call = 'define'; $extra = 997;
    $part = 'captured'; return $part . '-extra48';
}
$call = 'constant'; $effects = 0; $extra = 0; $result = 99;
echo 'B|';
try { $result = $call(constantArityFirst48(), constantArityExtra48()); echo 'BAD'; }
catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1] === 'captured-extra48' ? 'S' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $effects, '|', $call, '|', $extra, '|', $result;
''',
    'strict-defined-count-before-null-type-error-after-extra-effect': br'''<?php
declare(strict_types=1);
function strictQueryExtra48() { global $call, $effects; echo 'E|'; $call = 'constant'; $effects++; return 1073; }
$call = 'defined'; $effects = 0; $result = 99;
echo 'B|';
try { $result = $call(null, strictQueryExtra48()); echo 'BAD'; }
catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD', '|', $trace[0]['args'][1];
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $effects, '|', $call, '|', $result;
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
