"""Typed Exists verifies shared CVs before its truth consumer."""

CASES = [
    {
        'id': 'typed-bool-exists-shared-cv',
        'source': '''<?php
class ScalarReferenceExists implements ArrayAccess {
    public function &offsetExists($offset): bool {
        global $flag;
        echo "X:", $offset, ";";
        return $flag;
    }
    public function offsetGet($offset): mixed { echo "G;"; return 9; }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}
$box = new ScalarReferenceExists();
$flag = 1;
$alias =& $flag;
echo "I:", (int) isset($box[1]), ":", (int) ($flag === true), ":", (int) ($alias === true), ";";
$flag = 0;
echo "E:", (int) empty($box[2]), ":", (int) ($flag === false), ";";
$flag = 2;
echo "C:", $box[3] ?? 17, ":", (int) ($flag === true), ";";
$flag = null;
try { isset($box[4]); } catch (TypeError $error) { echo "T;"; }
echo "V:", (int) ($flag === null), ":", (int) ($alias === null), ";Z;";
''',
        'expected_stdout': 'I:X:1;1:1:1;E:X:2;1:1;C:X:3;G;9:1;X:4;T;V:1:1;Z;',
    },
]
