"""Discarded Get demand and a writable NULL reference from a void callback."""

CASES = [{
    'id': 'discarded-get-null-reference-review',
    'source': '''<?php
class VoidResultReview implements ArrayAccess {
    public function &offsetGet($offset): void {
        echo "G:", $offset, ";";
    }
    public function &offsetExists($offset): void {
        echo "E:", $offset, ";";
        return;
    }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}
$box = new VoidResultReview();
$box[1];
$alias =& $box[2];
echo "N:", $alias === null, ";";
$alias = 9;
echo "A:", $alias, ";";
$box->offsetGet(3);
echo "I:", isset($box[4]) ? 1 : 0, ";Z;";
''',
    'expected_stdout': 'G:1;G:2;N:1;A:9;G:3;I:E:4;0;Z;',
    'expected_diagnostics': [
        ('Deprecated', 'VoidResultReview::offsetGet(): Returning by reference from a void function is deprecated', 3),
        ('Deprecated', 'VoidResultReview::offsetExists(): Returning by reference from a void function is deprecated', 6),
        ('Deprecated', 'Return type of & VoidResultReview::offsetExists($offset): void should either be compatible with ArrayAccess::offsetExists(mixed $offset): bool, or the #[\\ReturnTypeWillChange] attribute should be used to temporarily suppress the notice', 6),
        ('Deprecated', 'Return type of & VoidResultReview::offsetGet($offset): void should either be compatible with ArrayAccess::offsetGet(mixed $offset): mixed, or the #[\\ReturnTypeWillChange] attribute should be used to temporarily suppress the notice', 3),
        ('Notice', 'Only variable references should be returned by reference', 5),
        ('Notice', 'Only variable references should be returned by reference', 5),
        ('Notice', 'Only variable references should be returned by reference', 5),
        ('Notice', 'Only variable references should be returned by reference', 8),
    ],
}]
