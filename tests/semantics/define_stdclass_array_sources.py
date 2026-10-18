#!/usr/bin/env python3
"""Native-first array snapshots with certified stdClass leaves."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'reference-snapshot-and-rebuilt-append-history': br'''<?php
echo 'B|';
const V66_LEAF = new stdClass();
$leaf = V66_LEAF;
$leaf->value = 3;
$cell = $leaf;
$input = [2 => &$cell, 5 => ['leaf' => &$cell]];
$input[90] = 'discard';
unset($input[90]);
echo define('V66_SNAPSHOT', $input) ? 'T|' : 'BAD|';
$cell = 41;
$snapshot = constant('V66_SNAPSHOT');
echo $snapshot[2] === $leaf && $snapshot[5]['leaf'] === $leaf ? 'I|' : 'BAD|';
echo $input[2], '|', $input[5]['leaf'], '|';
$snapshot[2]->value = 7;
echo V66_LEAF->value, '|';
$snapshot[] = 99;
echo isset($snapshot[6]) ? 'six|' : 'BAD|';
$input[] = 'later';
echo isset($input[91]) ? 'history|' : 'BAD|';
$bucket =& $snapshot[5]['leaf'];
$bucket = 23;
$again = constant('V66_SNAPSHOT');
echo $again[2] === $leaf && $again[5]['leaf'] === $leaf ? 'same|' : 'BAD|';
echo $again[5]['leaf']->value, '|';
unset($bucket, $input, $cell, $snapshot, $again, $leaf);
echo 'A|';
''',
    'selected-eval-nested-donor-snapshot': br'''<?php
echo 'B|';
const V66_EVAL_LEAF = new stdClass();
$leaf = V66_EVAL_LEAF;
$leaf->value = 11;
unset($leaf);
$install = 'define';
eval('$ok = $install("V66_EVAL_TREE", [4 => V66_EVAL_LEAF, 7 => ["leaf" => V66_EVAL_LEAF]]); echo $ok ? "T|" : "BAD|"; unset($ok);');
$get = 'constant';
$copy = $get(name: 'V66_EVAL_TREE');
$leaf = $copy[4];
$leaf->value = 19;
$copy[7]['leaf'] = 23;
$copy[7][] = 'tail';
$peer = $get('V66_EVAL_TREE');
echo $peer[4] === $leaf && $peer[7]['leaf'] === $leaf ? 'same|' : 'BAD|';
echo $peer[7]['leaf']->value, '|', $copy[7][0], '|';
echo isset($peer[7][0]) ? 'BAD|' : 'kept|';
echo V66_EVAL_LEAF->value, '|';
unset($copy, $peer, $leaf, $get, $install);
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
