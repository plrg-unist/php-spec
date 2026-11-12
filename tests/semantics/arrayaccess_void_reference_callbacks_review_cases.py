"""Swapped void boundaries preserve compiler deprecations and return Notices."""

CASES = [{
    'id': 'implicit-set-bare-unset-rhs-readback',
    'source': '''<?php
class VoidBoundaryRefReview implements ArrayAccess {
 public function offsetExists($offset): bool { return true; }
 public function offsetGet($offset): mixed { return 1; }
 public function &offsetSet($offset, $value): void {
  global $rhs;
  echo 'S:', $offset, ';';
  $rhs = 9;
 }
 public function &offsetUnset($offset): void {
  echo 'U:', $offset, ';';
  return;
 }
}
$box = new VoidBoundaryRefReview;
$rhs = 7;
$alias =& $rhs;
$out = ($box[1] = $rhs);
echo 'R:', $out, ':', $rhs, ':', $alias, ';';
unset($box[2]);
echo 'Z;';
''',
    'expected_stdout': 'S:1;R:9:9:9;U:2;Z;',
    'expected_diagnostics': [
        ('Deprecated', 'VoidBoundaryRefReview::offsetSet(): Returning by reference from a void function is deprecated', 5),
        ('Deprecated', 'VoidBoundaryRefReview::offsetUnset(): Returning by reference from a void function is deprecated', 10),
        ('Notice', 'Only variable references should be returned by reference', 9),
        ('Notice', 'Only variable references should be returned by reference', 12),
    ],
}]
