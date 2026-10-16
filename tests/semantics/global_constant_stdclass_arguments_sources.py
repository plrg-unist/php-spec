#!/usr/bin/env python3
"""Native-first ignored stdClass constant-AST arguments and abrupt retry."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'positional-named-donated-values': br'''<?php
echo 'B|';
const V63_DONOR = new stdClass();
const V63_VALUE = new stdClass(V63_DONOR, [NAN, [V63_DONOR, []]], spare: V63_DONOR, extra: [V63_DONOR]);
$donor = constant('V63_DONOR');
$donor->value = 17;
$first = constant('V63_VALUE');
$second = V63_VALUE;
echo $first === $second ? 'I' : 'BAD', '|', $first !== $donor ? 'D' : 'BAD', '|', isset($first->value) ? 'BAD' : 'empty';
$first->value = 23;
echo '|', $second->value, '|', $donor->value;
unset($first, $second, $donor);
$again = constant('V63_VALUE');
$kept = constant('V63_DONOR');
echo '|', $again !== $kept ? 'D' : 'BAD', '|', $again->value, '|', $kept->value, '|A|';
''',
    'eval-argument-error-and-fresh-retry': br'''<?php
echo 'B|';
const V63_DONOR = new stdClass();
$donor = V63_DONOR;
$donor->value = 31;
$code = 'const V63_RETRY = new stdClass(V63_DONOR, [NAN, [V63_DONOR]], V63_MISSING);';
try {
    eval($code);
    echo 'BAD';
} catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', defined('V63_RETRY') ? 'BAD' : 'absent';
}
define('V63_MISSING', 17);
eval($code);
$value = constant('V63_RETRY');
echo '|', $value !== $donor ? 'D' : 'BAD', '|', isset($value->value) ? 'BAD' : 'empty', '|', $donor->value, '|A|';
''',
}
family.BASELINE = ('global constant internal or Throwable initializer', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
