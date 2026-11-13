"""Quiet scalar retargets preserve initial-wrapper versus plain-slot history."""
from string_offset_request_callback_referenced_key_cases import CASES as INITIAL
from string_offset_request_callback_late_reference_cases import CASES as LATE


def changed(base, name, replacements, stdout):
    source = base['source']
    for old, new in replacements:
        source = source.replace(old, new)
    return dict(base, id='request-callback-scalar-key-' + name, source=source,
                expected_stdout=stdout)


CASES = [
    changed(INITIAL[0], 'initial-bool-payload', [
        ('    $replacementKey = 2;', '    $replacementKey = null;'),
        ('    $GLOBALS[$name] = 1;', '    $GLOBALS[$name] = true;'),
    ], '2:String offset cast occurred;R:b;B:99;K:;A:1;Z;'),
    changed(INITIAL[1], 'initial-null-payload', [
        ('    $replacementKey = 0;', '    $replacementKey = true;'),
        ('    $GLOBALS[$name] = 2;', '    $GLOBALS[$name] = null;'),
    ], '2:String offset cast occurred;R:a;B:99;K:1;A:;Z;'),
    changed(INITIAL[0], 'initial-float-payload', [
        ('    $replacementKey = 2;', '    $replacementKey = false;'),
        ('    $GLOBALS[$name] = 1;', '    $GLOBALS[$name] = 2.75;'),
        ('$key = false;', '$key = true;'),
    ], '2:String offset cast occurred;R:c;B:99;K:;A:2.75;Z;'),
    changed(LATE[0], 'plain-current-bool', [
        ('    $replacementKey = 2;', '    $replacementKey = true;'),
        ('    $GLOBALS[$name] = 1;', '    $GLOBALS[$name] = 2;'),
    ], '2:String offset cast occurred;R:b;B:99;K:1;A:2;Z;'),
    changed(LATE[1], 'plain-current-null', [
        ('    $replacementKey = 0;', '    $replacementKey = null;'),
    ], '2:String offset cast occurred;R:a;B:99;K:;A:2;Z;'),
    changed(LATE[0], 'plain-current-float', [
        ('    $replacementKey = 2;', '    $replacementKey = 2.75;'),
    ], '2:String offset cast occurred;R:c;B:99;K:2.75;A:1;Z;'),
]
