"""An initially undefined string key keeps CAST and live-key ordering."""

CASES = [{
    'id': 'defined-key-fixed-bounds',
    'source': '''<?php
function key_warning($level, $message, $file, $line) {
    $name = "missing";
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $GLOBALS[$name] = 1;
    } elseif ($message === "String offset cast occurred") {
        $GLOBALS[$name] = 5;
    } else {
        $GLOBALS[$name] = 0;
    }
    return true;
}
set_error_handler("key_warning");
echo "R:", "abc"[$missing], ";K:", $missing, ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;2:Uninitialized string offset 5;;K:0;Z;',
}]
