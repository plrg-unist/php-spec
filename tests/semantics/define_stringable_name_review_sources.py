#!/usr/bin/env python3
"""A throwing define-name conversion retains the raw receiver and earlier value."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-stringable-define-name-throw-keeps-raw-two-argument-trace': br'''<?php
class DefineStringReviewThrow55 {
    public function __toString(): string {
        global $call, $name, $value, $calls, $saved;
        echo 'S|'; $calls++;
        $call = 'constant'; $name = 'method-name55'; $value = 'method-value55';
        define('SOURCE55PEER', 1517);
        $saved = new Exception('string-name55-stop');
        throw $saved;
    }
}
function defineStringReviewValue55() {
    global $call, $name, $value, $effects;
    echo 'V|'; $effects++; $earlier = $value;
    $call = 'defined'; $name = 'argument-name55'; $value = 'argument-value55';
    return $earlier;
}
function defineStringReviewCaller55() {
    global $call, $name, $value, $calls, $effects, $saved;
    $call = 'DeFiNe'; $name = new DefineStringReviewThrow55(); $keep = $name;
    $prefix = 'captured-'; $value = $prefix . 'value55';
    $calls = 0; $effects = 0; $saved = null; $result = 99;
    try {
        $result = $call($name, defineStringReviewValue55());
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $e === $saved ? 'I' : 'BAD', '|', $e->getMessage();
        echo '|', $result, '|', $calls, '|', $effects, '|', $call, '|', $name, '|', $value;
        echo '|', $trace[0]['function'], '|', $trace[0]['class'], '|', $trace[0]['type'];
        echo '|', $trace[0]['args'] === [] ? 'E' : 'BAD';
        echo '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === $keep ? 'O' : 'BAD';
        echo '|', $trace[1]['args'][1] === 'captured-value55' ? 'V' : 'BAD';
        echo '|', $trace[2]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', constant('SOURCE55PEER'), '|', $result;
    } finally { echo '|Z'; }
}
echo 'B|'; defineStringReviewCaller55();
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
