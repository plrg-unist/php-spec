"""A literal NULL inner unset key warns before the unconditional nested Error."""

CASES = {
    'nested-unset-null-warning-named-handler-returns-true': b'''<?php
function nestedUnsetNullWarningReturn($level, $message, $file, $line) { echo "H:", $level, ":", $message, ";"; return true; }
$base = "ab"; $last = 0;
set_error_handler("nestedUnsetNullWarningReturn");
try { unset($base[null][$last = 7]); } catch (Throwable $error) { echo $error->getMessage(), "|", $error->getLine(), "|", $last, "|", $base, "|", (int)($error instanceof Error); }
''',
    'nested-unset-null-warning-named-handler-throws': b'''<?php
function nestedUnsetNullWarningThrow($level, $message, $file, $line) { echo "H:", $level, ":", $message, ";"; throw new Exception("handler"); }
$left = "ab"; $right = "cd"; $base = $left . $right; $last = 0;
set_error_handler("nestedUnsetNullWarningThrow");
try { unset($base[null][$last = 7]); } catch (Throwable $error) { echo $error->getMessage(), "|", $error->getLine(), "|", $last, "|", $base, "|", (int)($error instanceof Error); }
''',
}

OUTPUTS = dict(zip(CASES, (
    b'H:2:String offset cast occurred;Cannot use string offset as an array|5|7|ab|1',
    b'H:2:String offset cast occurred;handler|2|7|abcd|0',
)))

WATCHED = ('spec/semantics/30-storage.watsup', 'spec/semantics/38-array-unset.watsup',
           'spec/semantics/39-ownership.watsup', 'spec/semantics/43-array-unset-control.watsup',
           'spec/semantics/206-error-handlers.watsup', 'spec/semantics/207-error-handler-runtime.watsup',
           'spec/semantics/520-string-unset-warning-continuations.watsup')
