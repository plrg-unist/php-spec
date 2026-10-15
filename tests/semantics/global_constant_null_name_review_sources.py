#!/usr/bin/env python3
"""Independent abrupt null-name deprecation before API conversion."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'throwing-null-deprecation-keeps-raw-api-argument': br'''<?php
function stopNullQuery29($level, $message) {
    global $name, $call;
    echo 'H|', $level, '|', $message, '|';
    $name = 'changed';
    $call = 'defined';
    throw new Exception('stop');
}
function nullQueryCaller29() {
    global $name, $call;
    $name = null;
    $call = 'constant';
    $result = 99;
    set_error_handler('stopNullQuery29');
    try {
        $result = $call(name: $name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $name, '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === null ? 'N' : 'BAD';
        echo '|', $trace[2]['function'], '|', defined('') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
nullQueryCaller29();
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
