"""Reference-valued entries do not supply a current array's integer value."""

CASES = [{
    'id': 'undefined-current-array-alias-zero',
    'source': '''<?php
function currentAlias($level, $message) {
    $name = "missing";
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $GLOBALS[$name] = 0;
    } elseif ($message === "String offset cast occurred") {
        $value = 0;
        $GLOBALS[$name] = [&$value];
    }
    return true;
}
set_error_handler("currentAlias", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}, {
    # Independent: both entries own the same false-valued reference cell.
    'id': 'undefined-current-array-alias-shared-false-review',
    'source': '''<?php
function currentAliasReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $flag = false;
        $GLOBALS[$name] = [&$flag, &$flag];
    }
    return true;
}
set_error_handler("currentAliasReview", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}]
