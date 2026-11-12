"""Independent original: scalar parameter references and all quiet consumers."""

CASES = [{
    'id': 'untyped-parameter-reference-quiet-consumers',
    'source': '''<?php
class ExistsParameterReview implements ArrayAccess {
 #[ReturnTypeWillChange]
 public function &offsetExists(mixed $offset) { echo 'X:',(int)$offset,';'; return $offset; }
 public function offsetGet(mixed $offset): mixed { echo 'G;'; return 9; }
 public function offsetSet(mixed $offset,mixed $value): void {}
 public function offsetUnset(mixed $offset): void {}
}
$o=new ExistsParameterReview;
echo 'A:',(int)isset($o[false]),';';
echo 'B:',(int)isset($o[true]),';';
echo 'C:',(int)empty($o[false]),';';
echo 'D:',(int)empty($o[true]),';';
echo 'E:',$o[false]??17,';';
echo 'F:',$o[true]??17,';';
echo 'U;';isset($o[true]);empty($o[true]);$o[true]??17;echo 'Z;';
''',
    'expected_stdout': 'A:X:0;0;B:X:1;1;C:X:0;1;D:X:1;G;0;E:X:0;17;F:X:1;G;9;U;X:1;X:1;G;X:1;G;Z;',
}]
