"""A plain captured CV follows an absent name or its same ordinary text slot."""
from string_offset_request_callback_late_reference_cases import CASES as LATE
from string_offset_request_callback_rebound_key_cases import CASES as REBOUND

CASES = [dict(LATE[0],
    id='request-callback-plain-key-unset-after-late-alias',
    source=LATE[0]['source'].replace(
        '    $replacementKey = 2;\n    $GLOBALS[$name] =& $replacementKey;',
        '    unset($GLOBALS[$name]);').replace(
        '    $GLOBALS[$name] = 1;', '    $GLOBALS[$name] = 2;').replace(
        '$key = false;', '$key = true;').replace('";K:", $key', '";K:", isset($key)'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:;A:2;Z;',
    read_line=20),
    dict(REBOUND[1],
    id='request-callback-plain-key-same-ordinary-slot-text',
    source=REBOUND[1]['source'].replace(
        '    $replacementKey = 0;\n    $GLOBALS[$name] =& $replacementKey;',
        '    $GLOBALS[$name] = "2x";'),
    expected_stdout='2:String offset cast occurred;R:c;B:99;K:2x;Z;',
    read_line=21)]
