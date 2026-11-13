"""A genuine initial wrapper consumes its own raw payload after the Warning."""
from string_offset_request_callback_referenced_key_cases import CASES as REFERENCED
from string_offset_request_callback_old_key_cases import CASES as OLD

CASES = [dict(REFERENCED[1],
    id='request-callback-reference-raw-key-retarget',
    source=REFERENCED[1]['source'].replace(
        '    $replacementKey = 0;', '    $replacementKey = 2;').replace(
        '    $GLOBALS[$name] = 2;', '    $GLOBALS[$name] = $message;'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:2;A:String offset cast occurred;Z;',
    read_line=25),
    dict(OLD[1],
    id='request-callback-reference-raw-key-same-slot',
    source=OLD[1]['source'].replace(
        '    $GLOBALS[$name] = "2x";', '    $GLOBALS[$name] = $message;'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;A:String offset cast occurred;Z;',
    read_line=22)]
