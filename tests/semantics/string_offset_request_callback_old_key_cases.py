"""A captured live key wrapper does not depend on its current variable name."""
from string_offset_request_callback_rebound_key_cases import CONTROL
from string_offset_request_callback_text_key_cases import CASES as TEXT

CASES = [dict(CONTROL,
    id='request-callback-initial-reference-current-name-unset',
    source=CONTROL['source'].replace(
        '    $replacementKey = 2;\n    $GLOBALS[$name] =& $replacementKey;',
        '    unset($GLOBALS[$name]);').replace('";K:", $key', '";K:", isset($key)'),
    expected_stdout='2:String offset cast occurred;R:b;B:99;K:;A:1;Z;',
    read_line=20),
    dict(TEXT[1],
    id='request-callback-initial-reference-same-cell-text',
    source=TEXT[1]['source'].replace(
        '    $name = "key";\n    unset($GLOBALS[$name]);\n    $GLOBALS[$name] = "1";\n',
        '').replace('    $GLOBALS[$name] = "word";', '    $GLOBALS[$name] = "2x";'),
    expected_stdout='2:String offset cast occurred;R:c;B:99;K:2x;A:2x;Z;',
    read_line=22)]
