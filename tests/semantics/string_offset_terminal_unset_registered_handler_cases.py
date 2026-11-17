"""A registered error handler does not change terminal string UNSET_DIM."""

CASES = {
    'terminal-unset-registered-handler-interned-infinite-key': b'''<?php
function terminalUnsetRegisteredInternedHandler($level, $message, $file, $line) {
    echo "HANDLER:", $level, ":", $message, ";";
    return true;
}
$base = "ab";
$key = INF;
set_error_handler("terminalUnsetRegisteredInternedHandler");
try {
    unset($base[$key]);
} catch (Error $error) {
    echo $error->getMessage(), "|", $error->getLine(), "|", $base, "|", $key === INF ? "same" : "changed";
}
''',
    'terminal-unset-registered-handler-request-text-key': b'''<?php
function terminalUnsetRegisteredRequestHandler($level, $message, $file, $line) {
    echo "HANDLER:", $level, ":", $message, ";";
    return true;
}
$left = "ab";
$right = "cd";
$base = $left . $right;
$key = "bad";
set_error_handler("terminalUnsetRegisteredRequestHandler");
try {
    unset($base[$key]);
} catch (Error $error) {
    echo $error->getMessage(), "|", $error->getLine(), "|", $base, "|", $key === "bad" ? "same" : "changed";
}
''',
}

OUTPUTS = dict(zip(CASES, (
    b'Cannot unset string offsets|10|ab|same',
    b'Cannot unset string offsets|12|abcd|same',
)))

WATCHED = ('spec/semantics/38-array-unset.watsup',)
