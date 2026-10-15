#!/usr/bin/env python3
"""Ordinary string constant publication from actual source declarations."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-folded-and-alias': br'''<?php
namespace ConstString22;
echo 'B|';
const Literal = 'literal';
const EmptyValue = '';
const Folded = 'fold' . 'ed';
const AliasValue = Literal;
echo Literal, '|', EmptyValue === '' ? 'E' : 'BAD', '|', Folded, '|', AliasValue;
echo '|', \constant('cOnStStRiNg22\\Literal');
''',
    'request-string-alias': br'''<?php
$prefix = 'request';
define('RequestSource22', $prefix . '-value');
echo 'B|';
const RequestAlias22 = RequestSource22;
echo RequestAlias22, '|', constant('RequestAlias22');
''',
    'array-string-probe': br'''<?php
echo 'B|';
const StringArray22 = ['nested'];
echo StringArray22[0], '|A';
''',
}
family.BASELINE = ('global constant object transfer', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
