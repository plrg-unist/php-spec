#!/usr/bin/env python3
"""Independent nested empty copies freeze aliases before throwing trace writes."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-nested-empty-throw-late-flag-and-bucket-reference': br'''<?php
const V70_REVIEW_TARGET = 17;
$old = [90 => 'discard'];
unset($old[90]);
$next = [40 => 'discard'];
unset($next[40]);
$cell = $old;
$input = ['head' => &$cell, 'nested' => ['leaf' => &$cell]];
function v70ReviewThrow(int $level, string $message): bool {
    global $cell, $old;
    echo 'H|', $level, '|';
    $before = $cell;
    $before[] = 'probe';
    echo isset($before[41]) ? 'next|' : 'BAD|';
    unset($before);
    $cell = $old;
    define('V70_REVIEW_SIDE', 31);
    throw new Exception('V70_STOP');
}
set_error_handler('v70ReviewThrow');
$api = 'define';
$ok = 'kept';
echo 'B|';
try {
    $ok = $api(value: $input, case_insensitive: ($cell = $next) === null, constant_name: 'V70_REVIEW_TARGET');
    echo 'BAD|';
} catch (Exception $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo $trace[1]['function'], '|';
    echo $trace[1]['args'][2] === false ? 'false|' : 'BAD|';
    echo $raw['head'] === [] && $raw['nested']['leaf'] === [] ? 'empty|' : 'BAD|';
    $bucket =& $raw['nested']['leaf'];
    $bucket[] = 'trace';
    echo isset($raw['head'][91]) && !isset($raw['head'][0]) ? 'history|' : 'BAD|';
    echo $input['head'][91] === 'trace' && $input['nested']['leaf'][91] === 'trace' ? 'aliases|' : 'BAD|';
    echo $old === [] && $next === [] ? 'empty-cvs|' : 'BAD|';
    echo constant('V70_REVIEW_TARGET'), '|', constant('V70_REVIEW_SIDE'), '|', $ok, '|';
    unset($bucket, $trace, $raw, $error);
}
restore_error_handler();
unset($input, $cell, $old, $next, $api, $ok);
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
