#!/usr/bin/env python3
"""An early array-name capture keeps COW fields and live references distinct."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'captured-define-array-name-before-reference-and-true-flag-effects': br'''<?php
function defineArrayReviewValue52() {
    global $call, $name, $value, $cell, $effects;
    echo 'V|'; $effects++; $name['plain'] = 'value-live52';
    $cell = 1327; $call = 'constant';
    return $value;
}
function defineArrayReviewFlag52() {
    global $call, $name, $value, $cell, $flag, $effects;
    echo 'F|'; $effects++; $name['plain'] = 'flag-live52';
    $cell = 1361; $value = 997; $call = 'defined';
    return $flag;
}
function defineArrayReviewCaller52() {
    global $call, $name, $value, $cell, $flag, $effects;
    $call = 'DeFiNe'; $cell = 1307; $part = 'captured';
    $name = ['alias' => &$cell, 'plain' => $part . '-name52'];
    $value = $part . '-value52'; $flag = true; $effects = 0; $result = 99;
    try {
        $result = $call($name, defineArrayReviewValue52(), defineArrayReviewFlag52());
        echo 'BAD';
    } catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $result, '|', $effects, '|', $call;
        echo '|', $name['plain'], '|', $cell, '|', $value;
        echo '|', $trace[0]['function'], '|', $trace[0]['args'][0]['alias'];
        echo '|', $trace[0]['args'][0]['plain'] === 'captured-name52' ? 'C' : 'BAD';
        echo '|', $trace[0]['args'][1] === 'captured-value52' ? 'V' : 'BAD';
        echo '|', $trace[0]['args'][2] === true ? 'T' : 'BAD';
        echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', defined('Array') ? 'BAD' : 'A', '|', $result;
    } finally { echo '|Z'; }
}
echo 'B|'; defineArrayReviewCaller52();
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
