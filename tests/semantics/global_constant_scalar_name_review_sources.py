#!/usr/bin/env python3
"""Independent weak API argument conversion without caller-CV mutation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'false-cv-missing-error-and-converted-trace': br'''<?php
function missingScalarFalse27() {
    $query = false;
    $result = 99;
    $call = 'constant';
    try {
        $result = $call(name: $query);
        echo 'BAD';
    } catch (Error $e) {
        $trace = $e->getTrace();
        echo $query === false ? 'F' : 'D';
        echo '|', $result, '|', $e->getMessage(), '|', $e->getLine();
        echo '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === '' ? 'S' : 'D';
        echo '|', $trace[1]['function'];
    } finally {
        echo '|Z';
    }
}
echo 'B|';
missingScalarFalse27();
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
