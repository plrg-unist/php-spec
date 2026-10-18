#!/usr/bin/env python3
"""A loader throws only after a Stringable class query has replaced the API name."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-stringable-class-query-enters-loader-before-supplied-throw': br'''<?php
class StringQueryReviewName58 {
    public function __toString(): string {
        global $call, $name, $casts;
        echo 'S|'; $casts++; $call = 'defined'; $name = 'cast-name58';
        $part = 'AutoString'; return $part . 'Query58::VALUE';
    }
}
function stringQueryReviewLoader58($requested) {
    global $call, $name, $loads, $saved;
    echo 'L|', $requested, '|'; $loads++;
    $call = 'constant'; $name = 'loader-name58';
    define('SOURCE58PEER', 1699);
    $saved = new Exception('autoload58-stop'); throw $saved;
}
function stringQueryReviewCaller58() {
    global $call, $name, $casts, $loads, $saved;
    $call = 'CoNsTaNt'; $name = new StringQueryReviewName58(); $keep = $name;
    $casts = 0; $loads = 0; $saved = null; $result = 99;
    spl_autoload_register('stringQueryReviewLoader58');
    try { $result = $call($name); echo 'BAD'; }
    catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD', '|', $e->getMessage();
        echo '|', $result, '|', $casts, '|', $loads, '|', $call, '|', $name;
        echo '|', constant('SOURCE58PEER');
    } finally { echo '|Z'; }
    echo '|', $result;
}
echo 'B|'; stringQueryReviewCaller58();
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
