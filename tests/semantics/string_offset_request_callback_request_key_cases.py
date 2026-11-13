"""Late REQUEST text is owned by the current plain CV or the saved wrapper."""
from string_offset_request_callback_old_key_cases import CASES as OLD
from string_offset_request_callback_plain_key_cases import CASES as PLAIN

CASES = [dict(PLAIN[1],
    id='request-callback-request-key-current-ordinary',
    source=PLAIN[1]['source'].replace(
        '    $GLOBALS[$name] = "2x";',
        '    $keyLeft = "wo";\n    $keyRight = "rd";\n'
        '    $GLOBALS[$name] = $keyLeft . $keyRight;'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:word;Z;',
    read_line=23),
    dict(OLD[1],
    id='request-callback-request-key-old-reference',
    source=OLD[1]['source'].replace(
        '    $name = "alias";',
        '    $name = "key";\n    unset($GLOBALS[$name]);\n'
        '    $keyLeft = "2";\n    $keyRight = "x";\n    $name = "alias";').replace(
        '    $GLOBALS[$name] = "2x";',
        '    $GLOBALS[$name] = $keyLeft . $keyRight;').replace(
        '";K:", $key', '";K:", isset($key)'),
    expected_stdout='2:String offset cast occurred;R:c;B:99;K:;A:2x;Z;',
    read_line=26)]
