#!/usr/bin/env python3
"""Native-first query rejection of ordinary nonStringable and stdClass names."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'ordinary-object-query-names-reject-before-lookup': br'''<?php
class PlainQueryName54 {}
$name = new PlainQueryName54; $keep = $name; $result = 99;
echo 'B|';
try { $result = constant($name); echo 'BAD'; }
catch (TypeError $e) { echo $e->getMessage(), '|', $e->getLine(); }
try { $result = defined($name); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $result;
''',
    'selected-constant-object-name-keeps-earlier-receiver': br'''<?php
class SelectedPlainQuery54 {}
function plainQueryArgument54() {
    global $call, $name, $effects;
    $captured = $name; echo 'N|'; $effects++;
    $call = 'defined'; $name = 'live-name54'; return $captured;
}
function plainQueryCaller54() {
    global $call, $name, $effects;
    $call = 'CoNsTaNt'; $name = new SelectedPlainQuery54; $keep = $name;
    $effects = 0; $result = 99;
    try { $result = $call(plainQueryArgument54()); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
        echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
    }
    echo '|', $call, '|', $name, '|', $effects, '|', $result;
}
echo 'B|'; plainQueryCaller54();
''',
    'strict-stdclass-defined-rejects-after-argument-effects': br'''<?php
declare(strict_types=1);
function strictPlainQueryArgument54() {
    global $call, $name, $effects;
    $captured = $name; echo 'N|'; $effects++;
    $call = 'constant'; $name = 'strict-live54'; return $captured;
}
function strictPlainQueryCaller54() {
    global $call, $name, $effects;
    $call = 'DeFiNeD'; $name = new stdClass; $keep = $name;
    $effects = 0; $result = 99;
    try { $result = $call(strictPlainQueryArgument54()); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
        echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
    }
    echo '|', $call, '|', $name, '|', $effects, '|', $result;
}
echo 'B|'; strictPlainQueryCaller54();
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
