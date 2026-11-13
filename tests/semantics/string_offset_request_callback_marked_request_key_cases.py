"""Plain key history follows late marked REQUEST values in current CV cells."""
from string_offset_request_callback_late_reference_cases import CASES as LATE
from string_offset_request_callback_request_key_cases import CASES as REQUEST

CASES = [dict(LATE[1],
    id='request-callback-marked-request-key-retarget',
    source=LATE[1]['source'].replace(
        '    $replacementKey = 0;',
        '    $keyLeft = "wo";\n    $keyRight = "rd";\n'
        '    $replacementKey = $keyLeft . $keyRight;'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:word;A:2;Z;',
    read_line=27),
    dict(REQUEST[0],
    id='request-callback-marked-request-key-same-slot',
    source=REQUEST[0]['source'].replace(
        '    echo $level, ":", $message, ";";',
        '    echo $level, ":", $message, ";";\n'
        '    $GLOBALS["alias"] =& $GLOBALS["key"];').replace(
        '$keyLeft = "wo";', '$keyLeft = "2";').replace(
        '$keyRight = "rd";', '$keyRight = "x";').replace(
        '";K:", $key, ";Z;"', '";K:", $key, ";A:", $alias, ";Z;"'),
    expected_stdout='2:String offset cast occurred;R:c;B:99;K:2x;A:2x;Z;',
    read_line=24)]
