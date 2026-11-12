"""Strict string reference Get through an ordinary local CV."""

CASES = [{
    'id': 'strict-local-cv',
    'source': '''<?php
declare(strict_types=1);
class StringReferenceGet implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): string {
        $value = "alpha";
        if ($offset === 2) { $value = 17; }
        echo "G:", $offset, ";";
        return $value;
    }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}
$box = new StringReferenceGet();
echo "R:", $box[1], ";";
$alias =& $box[1];
echo "A:", $alias, ";";
$alias = 29;
echo "M:", $alias, ";";
try { $value = $box[2]; echo "BAD;"; }
catch (TypeError $error) { echo "T;"; }
echo "Z;";
''',
    'expected_stdout': 'R:G:1;alpha;G:1;A:alpha;M:29;G:2;T;Z;',
}]
