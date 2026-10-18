#!/usr/bin/env python3
"""Native-first Stringable query names, selected calls, and strict rejection."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'weak-stringable-query-names-before-global-lookup': br'''<?php
class QueryStringName53 {
    public function __toString(): string {
        global $calls;
        echo 'S|'; $calls++; return 'QueryStringValue53';
    }
}
const QueryStringValue53 = 1451;
$name = new QueryStringName53; $keep = $name; $calls = 0;
echo 'B|', constant($name), '|', defined($name) ? 'T' : 'BAD', '|', $calls;
''',
    'selected-stringable-constant-keeps-converted-missing-name': br'''<?php
class MissingQueryString53 {
    public function __toString(): string {
        global $call, $name, $calls;
        echo 'S|'; $calls++; $call = 'defined'; $name = 'live-name53';
        $prefix = 'Missing'; return $prefix . 'QueryString53';
    }
}
function queryMissingCaller53() {
global $call, $name, $calls;
$call = 'CoNsTaNt'; $name = new MissingQueryString53; $keep = $name;
$calls = 0; $result = 99;
try { $result = $call($name); echo 'BAD'; }
catch (Error $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === 'MissingQueryString53' ? 'S' : 'BAD';
    echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $call, '|', $name, '|', $calls, '|', $result;
}
echo 'B|'; queryMissingCaller53();
''',
    'strict-stringable-defined-rejects-before-method': br'''<?php
declare(strict_types=1);
class StrictQueryString53 {
    public function __toString(): string { echo 'BAD'; return 'TRUE'; }
}
function strictQueryArg53() {
    global $call, $name, $effects;
    echo 'N|'; $effects++; $call = 'constant'; return $name;
}
function queryStrictCaller53() {
global $call, $name, $effects;
$call = 'DeFiNeD'; $name = new StrictQueryString53; $keep = $name;
$effects = 0; $result = 99;
try { $result = $call(strictQueryArg53()); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
    echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $call, '|', $effects, '|', $result;
}
echo 'B|'; queryStrictCaller53();
''',
}
family.BASELINE = ('class constant value query', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
