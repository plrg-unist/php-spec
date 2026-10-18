#!/usr/bin/env python3
"""Native-first numeric unpack snapshots through retained intrinsic Closures."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-numeric-unpack-null-default-and-true-handler': br'''<?php
function ownedUnpackNullTrue66($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$call = ini_set(...); $keep = $call; $warnings = 0;
echo 'B|', $call(...[null, 2171]) === false ? 'F' : 'BAD';
set_error_handler('ownedUnpackNullTrue66', 8192);
echo '|', $keep->__invoke(...[null, 2183]) === false ? 'F' : 'BAD';
restore_error_handler(); echo '|', $warnings, '|', ini_get('precision');
''',
    'captured-owned-unpack-null-before-live-pack-mutation': br'''<?php
function ownedUnpackNullPack66() {
    global $call, $replacement, $pack, $value, $effects;
    $early = $pack; echo 'P|'; $effects++; ini_set('precision', '7');
    $call = $replacement; $pack = [31, 37]; $value = 'after-pack66'; return $early;
}
function ownedUnpackNullFalse66($level, $message) {
    global $call, $packKeep, $value, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8');
    $call = 'ini_get'; $packKeep[0] = 'precision'; $packKeep[1] = 'handler-pack66';
    $value = 'handler-value66'; return false;
}
function ownedUnpackNullCaller66() {
    global $call, $replacement, $pack, $packKeep, $value, $effects, $warnings;
    $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
    $part = 'packed'; $value = $part . '-value66'; $pack = [null, $value]; $packKeep = $pack;
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('ownedUnpackNullFalse66', 8192);
    try {
        $result = $call(...ownedUnpackNullPack66());
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision');
        echo '|', $effects, '|', $warnings, '|', $call, '|', $value;
        echo '|', $pack[0], '|', $pack[1], '|', $packKeep[0], '|', $packKeep[1];
        echo '|', $call === $keep ? 'BAD' : 'D';
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
}
echo 'B|'; ownedUnpackNullCaller66();
''',
    'strict-owned-unpack-null-before-weak-explicit-pack': br'''<?php
declare(strict_types=1);
function strictOwnedUnpackPack66() {
    global $call, $replacement, $pack, $effects;
    $early = $pack; echo 'P|'; $effects++; ini_set('precision', '9');
    $call = $replacement; $pack = [41, 43]; return $early;
}
function strictOwnedUnpackTrue66($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
function strictOwnedUnpackCaller66() {
    global $call, $replacement, $pack, $effects, $warnings;
    $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
    $pack = [null, 2213]; $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('strictOwnedUnpackTrue66', 8192);
    try {
        try { $result = $call(...strictOwnedUnpackPack66()); echo 'BAD'; }
        catch (TypeError $e) {
            echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings, '|', ini_get('precision');
        }
        echo '|E|'; $result = $keep->__invoke(...[null, 2221]);
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision'), '|', $warnings, '|', $effects;
        echo '|', $pack[0], '|', $pack[1];
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictOwnedUnpackCaller66();
''',
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'B|P|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
