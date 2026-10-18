#!/usr/bin/env python3
"""Native-first define() count errors before name and flag reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'too-few-define-arguments-preserve-null-and-caller-result': br'''<?php
$result = 99;
echo 'B|';
try { $result = define(); echo 'BAD'; }
catch (ArgumentCountError $e) { echo $e->getMessage(), '|', $e->getLine(); }
try { $result = define(null); echo 'BAD'; }
catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $result, '|', defined('') ? 'BAD' : 'U';
''',
    'selected-four-argument-define-keeps-raw-captures-after-effects': br'''<?php
function defineArityFirst49() {
    global $call, $effects, $name;
    echo 'N|'; $effects++; $call = 'defined'; return $name;
}
function defineArityFourth49() {
    global $call, $effects, $name, $value, $flag, $extra;
    echo 'E|'; $effects++; $saved = $extra;
    $call = 'constant'; $name = 'live-name49'; $value = 997; $flag = true; $extra = 'live-extra49';
    return $saved;
}
$call = 'define'; $name = null; $part = 'captured'; $value = $part . '-value49';
$flag = null; $extra = $part . '-extra49'; $effects = 0; $result = 99;
echo 'B|';
try { $result = $call(defineArityFirst49(), $value, $flag, defineArityFourth49()); echo 'BAD'; }
catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1] === 'captured-value49' ? 'V' : 'BAD';
    echo '|', $trace[0]['args'][2] === null ? 'F' : 'BAD';
    echo '|', $trace[0]['args'][3] === 'captured-extra49' ? 'X' : 'BAD';
    echo '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $effects, '|', $call, '|', $name, '|', $value, '|', $flag ? 'T' : 'BAD';
echo '|', $extra, '|', $result, '|', defined('') ? 'BAD' : 'U';
''',
    'strict-four-argument-define-count-before-null-type-rejection': br'''<?php
declare(strict_types=1);
function defineArityStrictExtra49() {
    global $call, $effects, $name, $flag;
    echo 'E|'; $effects++; $call = 'constant'; $name = 'strict-live49'; $flag = true;
    return 1103;
}
$call = 'define'; $name = null; $value = 1091; $flag = null; $effects = 0; $result = 99;
echo 'B|';
try { $result = $call($name, $value, $flag, defineArityStrictExtra49()); echo 'BAD'; }
catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1], '|', $trace[0]['args'][2] === null ? 'F' : 'BAD';
    echo '|', $trace[0]['args'][3], '|', $e->getPrevious() === null ? 'P' : 'BAD';
}
echo '|', $effects, '|', $call, '|', $result, '|', defined('') ? 'BAD' : 'U';
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
