"""Captured plain keys follow later-marked current INTERNED text after CAST."""
from string_offset_request_callback_late_reference_cases import CASES as LATE
from string_offset_request_callback_plain_key_cases import CASES as PLAIN

CASES = [dict(LATE[1],
    id='request-callback-marked-interned-key-retarget-word',
    source=LATE[1]['source'].replace(
        '    $replacementKey = 0;', '    $replacementKey = "word";'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:word;A:2;Z;',
    read_line=25),
    dict(PLAIN[1],
    id='request-callback-marked-interned-key-same-slot-numeric',
    source=PLAIN[1]['source'].replace(
        '    echo $level, ":", $message, ";";',
        '    echo $level, ":", $message, ";";\n'
        '    $GLOBALS["alias"] =& $GLOBALS["key"];').replace(
        '    $GLOBALS[$name] = "2x";', '    $GLOBALS[$name] = "2";').replace(
        '";K:", $key, ";Z;"', '";K:", $key, ";A:", $alias, ";Z;"'),
    expected_stdout='2:String offset cast occurred;R:c;B:99;K:2;A:2;Z;',
    read_line=22)]
