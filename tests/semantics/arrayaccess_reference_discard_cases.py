"""Language Set/Unset ignore reference results while preserving callback writes."""

CASES = [
    {
        'id': 'set-used-unused-append-and-direct',
        'source': '''<?php
class ReferenceSetDiscard implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function offsetGet($offset): mixed { return 0; }
    #[ReturnTypeWillChange]
    public function &offsetSet($offset, $value) {
        global $rhs;
        echo "S:", (int) $offset, ":", $value, ";";
        $rhs = 9;
        $value = 77;
        return $value;
    }
    public function offsetUnset($offset): void {}
}
$box = new ReferenceSetDiscard();
$rhs = 3;
$used = $box[1] = $rhs;
echo "A:", $used, ":", $rhs, ";";
$rhs = 5;
$box[2] = $rhs;
echo "B:", $rhs, ";";
$rhs = 6;
$box[] = $rhs;
echo "C:", $rhs, ";";
$direct = $box->offsetSet(3, 7);
echo "D:", $direct, ":", $rhs, ";";
''',
        'expected_stdout': 'S:1:3;A:9:9;S:2:5;B:9;S:0:6;C:9;S:3:7;D:77:9;',
    },
    {
        'id': 'unset-shared-cell-and-direct',
        'source': '''<?php
class ReferenceUnsetDiscard implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function offsetGet($offset): mixed { return 0; }
    public function offsetSet($offset, $value): void {}
    #[ReturnTypeWillChange]
    public function &offsetUnset($offset) {
        global $shared;
        $shared += 2;
        echo "U:", $offset, ":", $shared, ";";
        return $shared;
    }
}
$box = new ReferenceUnsetDiscard();
$shared = 3;
$alias =& $shared;
unset($box[1]);
echo "A:", $shared, ":", $alias, ";";
$direct = $box->offsetUnset(2);
echo "D:", $direct, ":", $shared, ":", $alias, ";";
$alias = 11;
echo "E:", $shared, ":", $alias, ":", $direct, ";";
''',
        'expected_stdout': 'U:1:5;A:5:5;U:2:7;D:7:7:7;E:11:11:7;',
    },
]
