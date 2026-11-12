"""Strict return verification handles a canonical plain-scalar union."""

CASES = [{
    'id': 'strict-float-bool-null-reference-get-cv',
    'source': '''<?php
declare(strict_types=1);
class ScalarUnionReferenceGetReview implements ArrayAccess {
 public function offsetExists(mixed $offset): bool { return true; }
 public function &offsetGet(mixed $offset): float|bool|null {
  echo 'G:', $offset, ';';
  $value = $offset;
  return $value;
 }
 public function offsetSet(mixed $offset, mixed $value): void {}
 public function offsetUnset(mixed $offset): void {}
}
$o = new ScalarUnionReferenceGetReview;
echo 'F:', (int)($o[17] === 17.0), ';';
echo 'B:', (int)($o[true] === true), ';';
echo 'N:', (int)($o[null] === null), ';';
try {
 echo 'S:', $o['2.5'], ';';
} catch (TypeError $e) {
 echo 'T;';
}
echo 'Z;';
''',
    'expected_stdout': 'F:G:17;1;B:G:1;1;N:G:;1;S:G:2.5;T;Z;',
}]
