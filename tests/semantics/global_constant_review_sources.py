#!/usr/bin/env python3
"""Independent late publication and startup-value lookup through constant()."""
from pathlib import Path

import global_constant_sources as family


SOURCE = br'''<?php
function publishGlobalReview21() {
    echo 'Q|';
    define('LateGlobalReview21', 'published');
    return '\\LateGlobalReview21';
}
echo 'B|';
$value = constant(name: publishGlobalReview21());
echo $value, '|', constant('E_WARNING');
'''

family.CASES = {'late-publication-and-startup': SOURCE}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
