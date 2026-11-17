"""Invalid nested STRING keys throw their own Error without handler entry."""

CASES = {
    'nested-unset-registered-handler-bad-text-before-missing-final-cv': b'''<?php
function nestedUnsetRegisteredBadText($level, $message, $file, $line) { echo "HANDLER:", $level, ":", $message, ";"; return true; }
$base = "ab";
set_error_handler("nestedUnsetRegisteredBadText");
try { unset($base["bad"][$missing]); } catch (Error $error) { echo $error->getMessage(), "|", $error->getLine(), "|", $base, "|", (int)isset($missing), "|", (int)($error instanceof TypeError); }
''',
    'nested-unset-registered-handler-request-live-floatlike-text-key': b'''<?php
function nestedUnsetRegisteredFloatlikeText($level, $message, $file, $line) { echo "HANDLER:", $level, ":", $message, ";"; return true; }
$left = "ab"; $right = "cd"; $base = $left . $right;
$key = "0x";
set_error_handler("nestedUnsetRegisteredFloatlikeText");
try { unset($base[$key][$key = "1.5"]); } catch (Error $error) { echo $error->getMessage(), "|", $error->getLine(), "|", $base, "|", $key, "|", (int)($error instanceof TypeError); }
''',
}

OUTPUTS = dict(zip(CASES, (
    b'Cannot unset string offsets|5|ab|0|0',
    b'Cannot unset string offsets|6|abcd|1.5|0',
)))

WATCHED = ('spec/semantics/38-array-unset.watsup',)
