#!/usr/bin/env python3
"""Independent raw string snapshots and carrier leaves survive abrupt reporting."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-raw-string-alias-copy-and-throwing-trace': br'''<?php
const V72_REVIEW_OLD = 17;
$old = ['word' => 'old', 'binary' => "O\0\xff", 'empty' => ''];
$next = ['word' => 'next', 'binary' => "N\0\x80", 'one' => 'x'];
$cell = $old;
$part = 'req';
$request = $part . '-leaf';
$input = ['head' => &$cell, 'again' => &$cell, 'request' => $request];
function v72ReviewThrow(int $level, string $message): bool {
    global $cell, $old;
    echo 'H|', $level, '|';
    $cell = $old;
    define('V72_REVIEW_SIDE', 31);
    throw new Exception('V72_STOP');
}
set_error_handler('v72ReviewThrow');
$api = 'define';
$ok = 'kept';
echo 'B|';
try {
    $ok = $api(value: $input, case_insensitive: ($cell = $next) === null, constant_name: 'V72_REVIEW_OLD');
    echo 'BAD|';
} catch (Exception $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo $trace[1]['function'], '|';
    echo $trace[1]['args'][2] === false ? 'false|' : 'BAD|';
    echo $raw['head']['word'], '|';
    echo $raw['head']['binary'] === "O\0\xff" && $raw['again']['empty'] === '' ? 'bytes|' : 'BAD|';
    echo $raw['request'] === 'req-leaf' ? 'request|' : 'BAD|';
    $bucket =& $raw['head']['binary'];
    $bucket = 'changed';
    unset($bucket);
    echo $input['again']['binary'], '|';
    echo $old['binary'] === "O\0\xff" && $next['binary'] === "N\0\x80" ? 'kept-cvs|' : 'BAD|';
    echo constant('V72_REVIEW_OLD'), '|', constant('V72_REVIEW_SIDE'), '|', $ok, '|';
    unset($trace, $raw, $error);
}
restore_error_handler();
unset($input, $cell, $old, $next, $part, $request, $api, $ok);
echo 'A|';
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
