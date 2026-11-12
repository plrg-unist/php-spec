"""Void Exists/Get preserve diagnostics and demanded NULL results."""

CASES = [
    {
        'id': 'void-exists-and-get-null-results',
        'source': '''<?php
class VoidResultCallbacks implements ArrayAccess {
    public function &offsetExists($offset): void {
        echo "E:", $offset, ";";
    }
    public function &offsetGet($offset): void {
        echo "G:", $offset, ";";
        return;
    }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}
$box = new VoidResultCallbacks();
echo "I:", (int) isset($box[1]), ";";
echo "M:", (int) empty($box[2]), ";";
echo "C:", $box[3] ?? 17, ";";
$value = $box[4];
echo "R:", (int) ($value === null), ";Z;";
''',
        'expected_stdout': 'I:E:1;0;M:E:2;1;C:E:3;17;G:4;R:1;Z;',
        'expected_diagnostics': [
            ('Deprecated', 'VoidResultCallbacks::offsetExists(): Returning by reference from a void function is deprecated', 3),
            ('Deprecated', 'VoidResultCallbacks::offsetGet(): Returning by reference from a void function is deprecated', 6),
            ('Deprecated', 'Return type of & VoidResultCallbacks::offsetExists($offset): void should either be compatible with ArrayAccess::offsetExists(mixed $offset): bool, or the #[\\ReturnTypeWillChange] attribute should be used to temporarily suppress the notice', 3),
            ('Deprecated', 'Return type of & VoidResultCallbacks::offsetGet($offset): void should either be compatible with ArrayAccess::offsetGet(mixed $offset): mixed, or the #[\\ReturnTypeWillChange] attribute should be used to temporarily suppress the notice', 6),
            ('Notice', 'Only variable references should be returned by reference', 5),
            ('Notice', 'Only variable references should be returned by reference', 5),
            ('Notice', 'Only variable references should be returned by reference', 5),
            ('Notice', 'Only variable references should be returned by reference', 8),
        ],
    },
]


def expected_stderr(case, source):
    return ''.join(level + ": " + message + " in " + str(source) + " on line " + str(line) + "\n"
                   for level, message, line in case['expected_diagnostics']).encode()
