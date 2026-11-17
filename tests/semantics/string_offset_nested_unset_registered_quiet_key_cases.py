"""Quiet nested string UNSET keys do not invoke registered error handlers."""

CASES = {
    'nested-unset-registered-handler-integer-before-missing-final-cv': b'''<?php
function nestedUnsetRegisteredQuietInteger($level, $message, $file, $line) { echo "HANDLER:", $level, ":", $message, ";"; return true; }
$base = "ab";
set_error_handler("nestedUnsetRegisteredQuietInteger");
try { unset($base[99][$missing]); } catch (Error $error) { echo $error->getMessage(), "|", $error->getLine(), "|", $base, "|", (int)isset($missing); }
''',
    'nested-unset-registered-handler-request-live-leading-key': b'''<?php
function nestedUnsetRegisteredQuietText($level, $message, $file, $line) { echo "HANDLER:", $level, ":", $message, ";"; return true; }
$left = "ab"; $right = "cd"; $base = $left . $right;
$key = "bad";
set_error_handler("nestedUnsetRegisteredQuietText");
try { unset($base[$key][$key = "0x"]); } catch (Error $error) { echo $error->getMessage(), "|", $error->getLine(), "|", $base, "|", $key; }
''',
}

OUTPUTS = dict(zip(CASES, (
    b'Cannot use string offset as an array|5|ab|0',
    b'Cannot use string offset as an array|6|abcd|0x',
)))

WATCHED = ('spec/semantics/38-array-unset.watsup',)
