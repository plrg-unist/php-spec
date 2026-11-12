"""A covariant reference return keeps the method's strict scalar check."""

CASES = [{
    'id': 'strict-integer-reference-get-cv',
    'source': '''<?php
declare(strict_types=1);
class StrictReferenceGetReview implements ArrayAccess {
 public function offsetExists(mixed $offset): bool { return true; }
 public function &offsetGet(mixed $offset): int {
  echo 'G:', $offset, ';';
  $value = $offset;
  return $value;
 }
 public function offsetSet(mixed $offset, mixed $value): void {}
 public function offsetUnset(mixed $offset): void {}
}
$o = new StrictReferenceGetReview;
echo 'R:', $o[11], ';';
try {
 echo 'S:', $o['12'], ';';
} catch (TypeError $e) {
 echo 'T;';
}
echo 'Z;';
''',
    'expected_stdout': 'R:G:11;11;S:G:12;T;Z;',
}]
