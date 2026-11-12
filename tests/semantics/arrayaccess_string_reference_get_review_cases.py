"""Strict string verification reads an ordinary CV with an existing alias."""

CASES = [{
    'id': 'strict-string-aliased-local-cv-review',
    'source': '''<?php
declare(strict_types=1);
class StringReferenceReview implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): string {
        echo "G:", $offset, ";";
        $value = 'beta';
        $inside =& $value;
        if ($offset === 2) { $inside = false; }
        return $value;
    }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}
$box = new StringReferenceReview();
$alias =& $box[1];
echo "A:", $alias, ";";
$alias = 31;
echo "M:", $alias, ";";
try { $box[2]; } catch (TypeError $error) { echo "T;"; }
echo "Z;";
''',
    'expected_stdout': 'G:1;A:beta;M:31;G:2;T;Z;',
}]
