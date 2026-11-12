"""Independent mixed-return callbacks retain shared scalar effects."""

CASES = [{
    'id': 'mixed-shared-property-callback-result-discarded',
    'source': '''<?php
class DiscardMixedReview implements ArrayAccess {
 public $returned = 41;
 public function offsetExists(mixed $offset): bool { return true; }
 public function offsetGet(mixed $offset): mixed { return 1; }
 #[ReturnTypeWillChange]
 public function &offsetSet(mixed $offset,mixed $value): mixed {
  global $rhs;
  echo 'S:',$offset,':',$value,';';
  $rhs=23;
  $this->returned=43;
  return $this->returned;
 }
 #[ReturnTypeWillChange]
 public function &offsetUnset(mixed $offset): mixed {
  global $rhs;
  echo 'U:',$offset,';';
  $rhs=29;
  $this->returned=47;
  return $this->returned;
 }
}
$o=new DiscardMixedReview;
$rhs=17;$alias=&$rhs;$returned=&$o->returned;
$out=($o[1]=$rhs);
echo 'V:',$out,':',$rhs,':',$alias,':',$returned,';';
unset($o[2]);
echo 'W:',$rhs,':',$alias,':',$returned,';';
echo 'D:',$o->offsetSet(3,5),';';
echo 'E:',$o->offsetUnset(4),';';
''',
    'expected_stdout': 'S:1:17;V:23:23:23:43;U:2;W:29:29:47;D:S:3:5;43;E:U:4;47;',
}]
