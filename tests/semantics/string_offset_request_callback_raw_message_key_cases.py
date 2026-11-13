"""A plain key consumes Warning message bytes stored in its late current wrapper."""
from string_offset_request_callback_late_reference_cases import CASES as LATE
from string_offset_request_callback_plain_key_cases import CASES as PLAIN

CASES = [dict(LATE[1],
    id='request-callback-raw-message-key-retarget',
    source=LATE[1]['source'].replace(
        '    $replacementKey = 0;', '    $replacementKey = $message;'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;A:2;Z;',
    read_line=25),
    dict(PLAIN[1],
    id='request-callback-raw-message-key-same-slot',
    source=PLAIN[1]['source'].replace(
        '    echo $level, ":", $message, ";";',
        '    echo $level, ":", $message, ";";\n'
        '    $GLOBALS["alias"] =& $GLOBALS["key"];').replace(
        '    $GLOBALS[$name] = "2x";', '    $GLOBALS[$name] = $message;').replace(
        '";K:", $key, ";Z;"', '";K:", $key, ";A:", $alias, ";Z;"'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;A:String offset cast occurred;Z;',
    read_line=22)]
