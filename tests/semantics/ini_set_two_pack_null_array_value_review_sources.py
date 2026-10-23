#!/usr/bin/env python3
"""Two completed unpack groups retain the early array through later COW."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-two-pack-array-captured-before-option-pack-and-cow': br'''<?php
function iniTwoPackNullArrayReviewOption86() {
    global $call, $option, $value, $arrayKeep, $valuePack, $effects;
    $earlier = $option; echo 'O|'; $effects++;
    $arrayKeep[0] = 'option-array86'; $valuePack['value'] = 0;
    $call = 'ini_get'; $value = 997; $option = 'precision';
    return ['option' => $earlier];
}
function iniTwoPackNullArrayReviewDeprecated86($level, $message) {
    global $call, $option, $value, $arrayKeep, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-array86';
    $call = 'constant'; $option = 'changed'; $value = 123;
    ini_set('precision', '10'); define('SOURCE86PEER', 3479);
    $saved = new Exception('two-pack-null-array86-stop'); throw $saved;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call; $option = null;
$seed = 'two-pack'; $value = [$seed . '-peer86']; $arrayKeep = $value;
$valuePack = ['value' => $value]; $packOld = $valuePack;
$effects = 0; $warnings = 0; $result = 99; $saved = null;
set_error_handler('iniTwoPackNullArrayReviewDeprecated86', 8192);
try { $result = $call(...$valuePack, ...iniTwoPackNullArrayReviewOption86()); echo 'BAD'; }
catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings;
    echo '|', $arrayKeep[0], '|', $valuePack['value'], '|', $packOld['value'][0];
    echo '|', constant('SOURCE86PEER');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '12'), '|', ini_get('precision'), '|', $result;
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
