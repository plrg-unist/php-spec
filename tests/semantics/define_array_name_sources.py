#!/usr/bin/env python3
"""Native-first array define names fail before optional flag reception or body."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-array-define-names-before-ignored-true-warning': br'''<?php
$result = 99;
echo 'B|';
try { $result = define([], 1301); echo 'BAD'; }
catch (TypeError $e) { echo $e->getMessage(), '|', $e->getLine(); }
try { $result = define([false, 1319], 1327, true); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0][0] === false ? 'F' : 'BAD';
    echo '|', $trace[0]['args'][0][1], '|', $trace[0]['args'][1];
    echo '|', $trace[0]['args'][2] === true ? 'T' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $result, '|', defined('') === false ? 'E' : 'BAD';
''',
    'captured-array-name-before-null-flag-reception': br'''<?php
function defineArrayValue52() {
    global $call, $name, $value, $effects;
    echo 'V|'; $effects++; $saved = $value;
    $call = 'constant'; $name['plain'] = 'live-name52'; $value = 997;
    return $saved;
}
function defineArrayFlag52() {
    global $call, $name, $flag, $effects;
    echo 'F|'; $effects++; $call = 'defined'; $name[4] = true; $flag = true;
    return null;
}
$call = 'DeFiNe'; $part = 'captured'; $value = $part . '-candidate52';
$name = ['plain' => $part . '-name52', 4 => false]; $flag = null;
$effects = 0; $result = 99;
echo 'B|';
try { $result = $call($name, defineArrayValue52(), defineArrayFlag52()); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0]['plain'] === 'captured-name52' ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][0][4] === false ? 'F' : 'BAD';
    echo '|', $trace[0]['args'][1] === 'captured-candidate52' ? 'V' : 'BAD';
    echo '|', $trace[0]['args'][2] === null ? 'Z' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $name['plain'], '|', $name[4] === true ? 'T' : 'BAD';
echo '|', $value, '|', $flag === true ? 'T' : 'BAD', '|', $call, '|', $effects, '|', $result;
''',
    'strict-array-define-name-before-third-integer-type-error': br'''<?php
declare(strict_types=1);
function defineArrayStrictFlag52() {
    global $call, $effects;
    echo 'F|'; $effects++; $call = 'constant'; return 17;
}
$call = 'define'; $effects = 0; $result = 99;
echo 'B|';
try { $result = $call([true, 1373], 1381, defineArrayStrictFlag52()); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0][0] === true ? 'T' : 'BAD';
    echo '|', $trace[0]['args'][0][1], '|', $trace[0]['args'][1], '|', $trace[0]['args'][2];
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $call, '|', $effects, '|', $result;
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
