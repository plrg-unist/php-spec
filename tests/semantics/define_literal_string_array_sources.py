#!/usr/bin/env python3
"""Native-first plain compiled string leaves in copied define array trees."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'compiled-literal-bytes-and-query-bucket-cow': br'''<?php
echo 'B|';
echo define('V72_TREE', ['plain' => 'alpha', 'nested' => ['empty' => '', 'one' => 'x', 'binary' => "A\0\xffB"]], false) ? 'T|' : 'BAD|';
$copy = constant('V72_TREE');
echo $copy['plain'] === 'alpha' && $copy['nested']['empty'] === '' && $copy['nested']['one'] === 'x' && $copy['nested']['binary'] === "A\0\xffB" ? 'bytes|' : 'BAD|';
$slot =& $copy['nested']['binary'];
$slot = 'local';
unset($slot);
$peer = constant('V72_TREE');
echo $copy['nested']['binary'], '|';
echo $peer['nested']['binary'] === "A\0\xffB" ? 'kept|' : 'BAD|';
echo $peer['plain'] === 'alpha' && $peer['nested']['one'] === 'x' ? 'same|' : 'BAD|';
unset($copy, $peer);
echo 'A|';
''',
    'selected-eval-literal-string-duplicate-and-original-trace': br'''<?php
const V72_OLD = 17;
$input = ['label' => 'before', 'nested' => ['word' => 'first', 'binary' => "B\0\xfe"]];
function v72Report($level, $message) {
    global $input;
    echo 'H|', constant('V72_OLD'), '|';
    $input['label'] = 'after';
    $input['nested']['word'] = 'second';
    $probe = new Exception('probe');
    $trace = $probe->getTrace();
    $raw = $trace[1]['args'][1];
    echo $raw['label'], '|', $raw['nested']['word'], '|';
    echo $raw['nested']['binary'] === "B\0\xfe" ? 'bytes|' : 'BAD|';
    unset($probe, $trace, $raw);
    return true;
}
set_error_handler('v72Report', E_WARNING);
echo 'B|';
eval('$api = "define"; $result = $api(value: $input, constant_name: "V72_OLD", case_insensitive: false); echo $result ? "BAD|" : "F|"; unset($api, $result);');
restore_error_handler();
echo $input['label'], '|', $input['nested']['word'], '|', constant('V72_OLD'), '|';
unset($input);
echo 'A|';
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
