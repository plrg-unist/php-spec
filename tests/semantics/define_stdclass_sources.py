#!/usr/bin/env python3
"""Native-first define of certified stdClass donors and duplicate callbacks."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'named-donor-publication-and-alias-release': br'''<?php
echo 'B|';
const V65_DONOR = new stdClass();
$donor = V65_DONOR;
$donor->value = 3;
echo define(value: $donor, constant_name: 'V65_PUBLISHED') ? 'T|' : 'BAD|';
$first = constant(name: 'V65_PUBLISHED');
$peer = constant('V65_DONOR');
echo $first === $donor && $peer === $first ? 'I|' : 'BAD|';
$first->value = 7;
echo V65_PUBLISHED->value, '|', V65_DONOR->value, '|';
unset($donor, $first, $peer);
$again = constant('V65_PUBLISHED');
echo $again === V65_DONOR ? 'same|' : 'BAD|';
echo $again->value, '|';
unset($again);
echo 'A|';
''',
    'selected-eval-duplicate-and-handler-mutation': br'''<?php
echo 'B|';
const V65_OLD = new stdClass();
const V65_NEXT = new stdClass();
V65_OLD->value = 11;
V65_NEXT->value = 29;
$install = 'define';
echo $install(constant_name: 'V65_DUPLICATE', value: V65_OLD, case_insensitive: false) ? 'T|' : 'BAD|';
set_error_handler(function ($level, $message) {
    echo 'H|', $level, '|', $message, '|';
    V65_OLD->value = 13;
    V65_NEXT->value = 31;
    define('V65_HANDLER_SIDE', 19);
    return true;
});
eval('$install = "define"; $candidate = V65_NEXT; $result = $install(value: $candidate, constant_name: "V65_DUPLICATE", case_insensitive: false); echo $result ? "BAD|" : "F|"; unset($candidate, $result);');
restore_error_handler();
$held = constant('V65_DUPLICATE');
echo $held === V65_OLD ? 'old|' : 'BAD|';
echo V65_DUPLICATE->value, '|', V65_NEXT->value, '|', V65_HANDLER_SIDE, '|';
unset($held, $install);
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
