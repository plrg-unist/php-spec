#!/usr/bin/env python3
"""An array-name TypeError preserves reference leaves across trace-array COW."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-array-query-trace-shares-scalar-reference-after-cow': br'''<?php
function queryArrayReviewArgument51() {
    global $call, $name, $effects;
    echo 'A|'; $effects++; $call = 'constant';
    return $name;
}
function queryArrayReviewCaller51() {
    global $call, $name, $effects;
    $call = 'DeFiNeD'; $cell = 1237; $part = 'captured';
    $name = ['alias' => &$cell, 'plain' => $part . '-plain51'];
    $effects = 0; $result = 99;
    try {
        $result = $call(queryArrayReviewArgument51());
        echo 'BAD';
    } catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $result, '|', $effects, '|', $call;
        echo '|', $trace[0]['function'], '|', $trace[0]['args'][0]['alias'];
        echo '|', $trace[0]['args'][0]['plain'] === 'captured-plain51' ? 'C' : 'BAD';
        $name['plain'] = 'live-plain51'; $cell = 1249;
        echo '|', $trace[0]['args'][0]['alias'];
        echo '|', $trace[0]['args'][0]['plain'] === 'captured-plain51' ? 'C' : 'BAD';
        echo '|', $name['plain'] === 'live-plain51' ? 'L' : 'BAD';
        $trace[0]['args'][0]['alias'] = 1277;
        echo '|', $cell, '|', $name['alias'];
        echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', $result;
    } finally { echo '|Z'; }
}
echo 'B|'; queryArrayReviewCaller51();
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
