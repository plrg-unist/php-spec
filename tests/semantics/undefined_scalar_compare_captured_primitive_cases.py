"""Captured primitive Boolean operands and explicit owning boundaries."""

CASES = {
    'captured-equal-right-zero': b'''<?php
$value = 0;
$calls = 0;
function capturedEqualScalar113($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['value'] = 7;
    $GLOBALS['saved'] = 9;
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('capturedEqualScalar113');
$result = $missing == ($saved = $value);
echo 'R:', $result === true, ':', $value === 7, ':', $saved === 9, ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'captured-greater-left-string': b'''<?php
$value = '0';
$calls = 0;
function capturedGreaterScalar113($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['value'] = 7;
    $GLOBALS['saved'] = '';
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('capturedGreaterScalar113');
$result = ($saved = $value) > $missing;
echo 'R:', $result === true, ':', $value === 7, ':', $saved === '', ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'captured-not-equal-float-null-no-init': b'''<?php
$number = 0.0;
$null = null;
$calls = 0;
function capturedFloatNull113($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $line, ':', $calls, ';';
    $GLOBALS['number'] = 7.0;
    $GLOBALS['savedFloat'] = 7.0;
    $GLOBALS['null'] = 7;
    $GLOBALS['savedNull'] = 7;
    return true;
}
set_error_handler('capturedFloatNull113');
$a = $floatMissing != ($savedFloat = $number);
$null = null;
$b = ($savedNull = $null) == $nullMissing;
echo 'R:', $a === false, ':', $b === true, ':', $calls === 2, ':', !isset($floatMissing), ':', !isset($nullMissing), ':', $number === 7.0, ':', $savedFloat === 7.0, ':', $null === 7, ':', $savedNull === 7, ';END;';
''',
    'captured-less-less-equal-no-init': b'''<?php
$text = '0';
$flag = false;
$calls = 0;
function capturedForward113($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $line, ':', $calls, ';';
    $GLOBALS['text'] = '';
    $GLOBALS['savedText'] = '';
    $GLOBALS['flag'] = true;
    $GLOBALS['savedFlag'] = true;
    return true;
}
set_error_handler('capturedForward113');
$a = $textMissing < ($savedText = $text);
$flag = false;
$b = ($savedFlag = $flag) <= $flagMissing;
echo 'R:', $a === true, ':', $b === true, ':', $calls === 2, ':', !isset($textMissing), ':', !isset($flagMissing), ':', $text === '', ':', $savedText === '', ':', $flag === true, ':', $savedFlag === true, ';END;';
''',
    'captured-greater-equal-bool-default': b'''<?php
$value = true;
$calls = 0;
function capturedBoolDefault113($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['value'] = false;
    $GLOBALS['saved'] = false;
    $GLOBALS['missing'] = true;
    return false;
}
set_error_handler('capturedBoolDefault113');
$result = $missing >= ($saved = $value);
echo 'R:', $result === false, ':', $value === false, ':', $saved === false, ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'captured-not-equal-supplied-throw': b'''<?php
$value = 1;
$chosen = new Exception('chosen113');
$calls = 0;
$result = 41;
function capturedNotEqualThrow113($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['value'] = 0;
    $GLOBALS['saved'] = 0;
    $GLOBALS['missing'] = 9;
    throw $GLOBALS['chosen'];
}
set_error_handler('capturedNotEqualThrow113');
try {
    $result = $missing != ($saved = $value);
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $chosen, ':', $result === 41, ':', $value === 0, ':', $saved === 0, ':', $missing === 9, ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
echo 'END;';
''',
    'captured-object-boundary': b'''<?php
function capturedObjectBoundary113($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('capturedObjectBoundary113');
echo 'B|';
$result = (new Exception('captured113')) == $missing;
echo $result ? '1' : '0';
''',
    'captured-nested-boundary': b'''<?php
function capturedNestedBoundary113($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('capturedNestedBoundary113');
echo 'B|';
$result = $missing <= [[false]];
echo $result ? '1' : '0';
''',
}
