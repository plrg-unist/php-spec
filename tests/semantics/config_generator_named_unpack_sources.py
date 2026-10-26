#!/usr/bin/env python3
"""Named keys streamed by a source Generator into CONFIG ini_set."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'named-option-then-value': br'''<?php
function namedConfig97() {
    echo 'Y0|'; yield 'option' => 'precision';
    echo 'Y1|'; yield 'value' => '8';
    echo 'Y2|';
}
$generator = namedConfig97(); $result = 99; echo 'B|';
$result = ini_set(...$generator);
echo 'R|', $result, '|', ini_get('precision');
''',
    'named-value-then-option': br'''<?php
function reversedConfig97() {
    echo 'Y0|'; yield 'value' => '7';
    echo 'Y1|'; yield 'option' => 'precision';
    echo 'Y2|';
}
$generator = reversedConfig97(); $result = 99; echo 'B|';
$result = ini_set(...$generator);
echo 'R|', $result, '|', ini_get('precision');
''',
    'duplicate-named-stops-before-next': br'''<?php
function duplicateConfig97() {
    echo 'Y0|'; yield 'option' => 'precision';
    echo 'Y1|'; yield 'option' => 'output_buffering';
    echo 'BAD-Y2|';
}
$generator = duplicateConfig97(); $result = 99; echo 'B|';
try { $result = ini_set(...$generator); echo 'BAD-CALL|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $result, '|', ini_get('precision'); }
''',
    'unknown-named-stops-before-next': br'''<?php
function unknownConfig97() {
    echo 'Y0|'; yield 'other' => 'precision';
    echo 'BAD-Y1|';
}
$generator = unknownConfig97(); $result = 99; echo 'B|';
try { $result = ini_set(...$generator); echo 'BAD-CALL|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $result, '|', ini_get('precision'); }
''',
    'named-then-numeric-string-stops-before-next': br'''<?php
function mixedConfig97() {
    echo 'Y0|'; yield 'option' => 'precision';
    echo 'Y1|'; yield '0' => '8';
    echo 'BAD-Y2|';
}
$generator = mixedConfig97(); $result = 99; echo 'B|';
try { $result = ini_set(...$generator); echo 'BAD-CALL|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $result, '|', ini_get('precision'); }
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Generator unpack send outside two-string integer-key domain', b'B|Y0|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
