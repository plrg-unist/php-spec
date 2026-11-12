"""Typed reference Get verifies CVs before returning an unconstrained reference."""

CASES = [
    {
        'id': 'int-cv-reference-and-weak-check',
        'source': '''<?php
class TypedReferenceGet implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): int {
        echo "G:", $offset, ";";
        $value = $offset;
        return $value;
    }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}
$box = new TypedReferenceGet();
echo "R:", $box[17], ";";
$reference =& $box[23];
echo "A:", $reference, ";";
$reference = "free";
echo "F:", $reference, ";";
$weak = $box["19"];
echo "W:", $weak, ";";
try { $box["bad"]; } catch (TypeError $error) { echo "T;"; }
''',
        'expected_stdout': 'R:G:17;17;G:23;A:23;F:free;G:19;W:19;G:bad;T;',
    },
]
