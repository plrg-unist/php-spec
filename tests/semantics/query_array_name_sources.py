#!/usr/bin/env python3
"""Native-first query array names reject before lookup and retain trace ownership."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-empty-array-query-names': br'''<?php
$result = 99;
echo 'B|';
try { $result = defined([]); echo 'BAD'; }
catch (TypeError $e) { echo $e->getMessage(), '|', $e->getLine(); }
try { $result = constant([]); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === [] ? 'A' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $result;
''',
    'selected-constant-array-name-keeps-captured-cow-value': br'''<?php
function queryArrayName51() {
    global $call, $name, $effects;
    echo 'N|'; $effects++; $call = 'defined'; return $name;
}
$call = 'CoNsTaNt'; $part = 'captured'; $leaf = $part . '-array51';
$name = ['first' => $leaf, 3 => null]; $snapshot = $name;
$effects = 0; $result = 99;
echo 'B|';
try { $result = $call(queryArrayName51()); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0]['first'] === 'captured-array51' ? 'S' : 'BAD';
    echo '|', $trace[0]['args'][0][3] === null ? 'N' : 'BAD';
    $name['first'] = 'caller-array51';
    echo '|', $trace[0]['args'][0]['first'] === 'captured-array51' ? 'C' : 'BAD';
    $trace[0]['args'][0]['first'] = 'trace-array51';
    echo '|', $name['first'], '|', $snapshot['first'];
    echo '|', $trace[0]['args'][0]['first'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $call, '|', $effects, '|', $result;
''',
    'strict-defined-flat-array-name-type-error': br'''<?php
declare(strict_types=1);
$result = 99;
echo 'B|';
try { $result = defined([true, 1277, 1.5]); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0][0] === true ? 'T' : 'BAD';
    echo '|', $trace[0]['args'][0][1], '|', $trace[0]['args'][0][2] === 1.5 ? 'D' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $result;
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
