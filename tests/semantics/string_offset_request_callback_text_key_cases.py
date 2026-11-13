"""Text installed after a cast Warning uses the already selected key history."""
from string_offset_request_callback_ordinary_key_cases import CASES as ORDINARY

CASES = [dict(ORDINARY[0],
    id='request-callback-plain-current-leading-text',
    source=ORDINARY[0]['source'].replace(
        '    $GLOBALS[$name] = 2;', '    $GLOBALS[$name] = "2x";'),
    expected_stdout='2:String offset cast occurred;R:c;B:99;K:2x;A:1;Z;'),
    dict(ORDINARY[1],
    id='request-callback-initial-reference-nonnumeric-text',
    source=ORDINARY[1]['source'].replace(
        '    $GLOBALS[$name] = 0;', '    $GLOBALS[$name] = "1";').replace(
        '    $GLOBALS[$name] = 2;', '    $GLOBALS[$name] = "word";'),
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:1;A:word;Z;')]
