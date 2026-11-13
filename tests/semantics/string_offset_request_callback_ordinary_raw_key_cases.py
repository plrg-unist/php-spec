"""A plain key follows raw Warning message text in its ordinary current CV."""
from string_offset_request_callback_late_reference_cases import CASES as LATE
from string_offset_request_callback_plain_key_cases import CASES as PLAIN

CASES = [dict(LATE[1],
    id='request-callback-ordinary-raw-key-retarget',
    source=LATE[1]['source'].replace(
        '    $replacementKey = 0;\n    $GLOBALS[$name] =& $replacementKey;',
        '    unset($GLOBALS[$name]);\n    $GLOBALS[$name] = $message;'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;A:2;Z;',
    read_line=25),
    dict(PLAIN[1],
    id='request-callback-ordinary-raw-key-same-slot',
    source=PLAIN[1]['source'].replace(
        '    $GLOBALS[$name] = "2x";', '    $GLOBALS[$name] = $message;'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;Z;',
    read_line=21)]
