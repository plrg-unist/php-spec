"""Handler-created flat arrays remain live against a missing-read NULL."""

CASES = {
    'array-resume-missing-left-empty': b'''<?php
$right = 2; $calls = 0;
function arrayResume108($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['missing'] = 9; $GLOBALS['right'] = [];
    return true;
}
set_error_handler('arrayResume108');
$result = $missing <=> $right;
echo 'R:', $result === 0, ':', $right === [], ':', $missing === 9, ':', $calls === 1, ';';
$right[] = 7; echo 'A:', $right[0] === 7, ':', $result === 0, ';END;';
''',
    'array-resume-missing-right-empty': b'''<?php
$left = 2; $calls = 0;
function arrayResume108($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['left'] = []; $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('arrayResume108');
$result = $left <=> $missing;
echo 'R:', $result === 0, ':', $left === [], ':', $missing === 9, ':', $calls === 1, ';';
$left[] = 7; echo 'A:', $left[0] === 7, ':', $result === 0, ';END;';
''',
    'array-resume-flat-primitive-tags': b'''<?php
$right = 0; $calls = 0;
function arrayTags108($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['right'] = [null, false, 7, 1.5, 'text'];
    return true;
}
set_error_handler('arrayTags108');
$result = $missing <=> $right;
echo 'R:', $result === -1, ':', $right[0] === null, ':', $right[1] === false, ':', $right[2] === 7, ':', $right[3] === 1.5, ':', $right[4] === 'text', ':', !isset($missing), ':', $calls === 1, ';END;';
''',
    'array-resume-same-name-nonempty': b'''<?php
$calls = 0;
function arraySame108($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $x', ':', $line, ':', $calls, ';';
    $GLOBALS['x'] = [false]; return true;
}
set_error_handler('arraySame108');
$result = $x <=> $x;
echo 'R:', $result === -1, ':', $x[0] === false, ':', $calls === 1, ';END;';
''',
    'array-resume-initial-array-boundary': b'''<?php
function arrayInitial108($level, $message, $file, $line) {
    echo 'H|'; $GLOBALS['missing'] = 9; $GLOBALS['right'] = []; return true;
}
$right = [1];
set_error_handler('arrayInitial108');
echo 'B|'; $result = $missing <=> $right; echo $result;
''',
    'array-resume-nested-array-boundary': b'''<?php
function arrayNested108($level, $message, $file, $line) {
    echo 'H|'; $GLOBALS['missing'] = 9; $GLOBALS['right'] = [[1]]; return true;
}
$right = 0;
set_error_handler('arrayNested108');
echo 'B|'; $result = $missing <=> $right; echo $result;
''',
}
