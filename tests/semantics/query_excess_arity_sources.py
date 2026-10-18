#!/usr/bin/env python3
"""Native-first excess query arguments before string reception and lookup."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-excess-query-counts-before-null-reception': br'''<?php
$result = 99;
echo 'B|';
try { $result = defined(null, 1117, true); echo 'BAD'; }
catch (ArgumentCountError $e) { echo $e->getMessage(), '|', $e->getLine(); }
try { $result = constant(null, 1123, false, 1147); echo 'BAD'; }
catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1], '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
    echo '|', $trace[0]['args'][3], '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $result;
''',
    'selected-constant-three-arguments-retain-earlier-captures': br'''<?php
function queryExcessFirst50() {
    global $call, $effects, $name;
    echo 'N|'; $effects++; $call = 'defined'; return $name;
}
function queryExcessLast50() {
    global $call, $effects, $name, $extra;
    echo 'E|'; $effects++; $call = 'define'; $name = 'live-name50'; $extra = 997;
    return 1151;
}
$call = 'constant'; $name = null; $part = 'captured'; $extra = $part . '-extra50';
$effects = 0; $result = 99;
echo 'B|';
try { $result = $call(queryExcessFirst50(), $extra, queryExcessLast50()); echo 'BAD'; }
catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1] === 'captured-extra50' ? 'S' : 'BAD';
    echo '|', $trace[0]['args'][2], '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $effects, '|', $call, '|', $name, '|', $extra, '|', $result;
''',
    'strict-defined-five-arguments-count-before-null-type-error': br'''<?php
declare(strict_types=1);
function queryExcessStrictLast50() {
    global $call, $effects;
    echo 'E|'; $effects++; $call = 'constant'; return 1181;
}
$call = 'defined'; $effects = 0; $result = 99;
echo 'B|';
try { $result = $call(null, 1163, true, 1171, queryExcessStrictLast50()); echo 'BAD'; }
catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1], '|', $trace[0]['args'][2] === true ? 'T' : 'BAD';
    echo '|', $trace[0]['args'][3], '|', $trace[0]['args'][4];
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
