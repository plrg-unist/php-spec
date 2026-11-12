"""Ignored callback result slots still verify and write shared scalar CVs."""

CASES = [{
    'id': 'strict-shared-cv-set-unset-verification',
    'source': '''<?php
declare(strict_types=1);
class ScalarDiscardReferenceReview implements ArrayAccess {
 public function offsetExists(mixed $offset): bool { return true; }
 public function offsetGet(mixed $offset): mixed { return 7; }
 #[ReturnTypeWillChange]
 public function &offsetSet(mixed $offset, mixed $value): float {
  global $shared;
  echo 'S:', $offset, ';';
  return $shared;
 }
 #[ReturnTypeWillChange]
 public function &offsetUnset(mixed $offset): float {
  global $shared;
  echo 'U:', $offset, ';';
  return $shared;
 }
}
$box = new ScalarDiscardReferenceReview;
$shared = 17;
$alias =& $shared;
$out = ($box[1] = $shared);
echo 'A:', (int)($out === 17.0), ':', (int)($shared === 17.0), ':', (int)($alias === 17.0), ';';
$shared = 19;
$box[2] = 5;
echo 'B:', (int)($shared === 19.0), ':', (int)($alias === 19.0), ';';
$shared = 23;
unset($box[3]);
echo 'C:', (int)($shared === 23.0), ':', (int)($alias === 23.0), ';';
$shared = 'bad';
try {
 unset($box[4]);
} catch (TypeError $e) {
 echo 'T;';
}
echo 'D:', $shared, ':', $alias, ';Z;';
''',
    'expected_stdout': 'S:1;A:1:1:1;S:2;B:1:1;U:3;C:1:1;U:4;T;D:bad:bad;Z;',
}]
