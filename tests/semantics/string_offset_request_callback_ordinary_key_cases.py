"""Unsetting and assigning a global key creates an ordinary current cell."""
from string_offset_request_callback_late_reference_cases import CASES as LATE
from string_offset_request_callback_referenced_key_cases import CASES as INITIAL

CASES = [dict(LATE[0],
    id='request-callback-plain-cv-follows-ordinary-replacement',
    source=LATE[0]['source'].replace(
        '    $replacementKey = 2;\n    $GLOBALS[$name] =& $replacementKey;',
        '    unset($GLOBALS[$name]);\n    $GLOBALS[$name] = 2;')),
    dict(INITIAL[1],
    id='request-callback-initial-reference-keeps-old-with-ordinary-current',
    source=INITIAL[1]['source'].replace(
        '    $replacementKey = 0;\n    $GLOBALS[$name] =& $replacementKey;',
        '    unset($GLOBALS[$name]);\n    $GLOBALS[$name] = 0;'))]
