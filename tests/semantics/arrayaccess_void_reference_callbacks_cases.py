"""Bare Set and implicit Unset retain void-reference diagnostics."""

CASES = [
    {
        'id': 'bare-set-implicit-unset-void',
        'source': '''<?php
class VoidReferenceCallbacks implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function offsetGet($offset): mixed { return 0; }
    public function &offsetSet($offset, $value): void {
        echo "S:", $offset, ":", $value, ";";
        return;
    }
    public function &offsetUnset($offset): void {
        echo "U:", $offset, ";";
    }
}
$box = new VoidReferenceCallbacks();
$rhs = 17;
$used = $box[1] = $rhs;
echo "A:", $used, ":", $rhs, ";";
unset($box[2]);
echo "Z;";
''',
        'expected_stdout': 'S:1:17;A:17:17;U:2;Z;',
        'expected_diagnostics': [
            ('Deprecated', 'VoidReferenceCallbacks::offsetSet(): Returning by reference from a void function is deprecated', 5),
            ('Deprecated', 'VoidReferenceCallbacks::offsetUnset(): Returning by reference from a void function is deprecated', 9),
            ('Notice', 'Only variable references should be returned by reference', 7),
            ('Notice', 'Only variable references should be returned by reference', 11),
        ],
    },
]


def expected_stderr(case, source):
    return ''.join(level + ": " + message + " in " + str(source) + " on line " + str(line) + "\n"
                   for level, message, line in case['expected_diagnostics']).encode()
