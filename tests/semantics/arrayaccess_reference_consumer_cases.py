"""New consumer originals; expectations need recorded native/model agreement."""

CASES = [
    {
        'id': 'direct-named-reference-get-keeps-real-property-cell',
        'source': '''<?php
function directNamed326(&$value) { echo "F:", $value, ";"; $value = 8; }
class DirectNamedGet326 implements ArrayAccess {
    public $data = 7;
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return $this->data; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new DirectNamedGet326();
directNamed326(value: $box['slot']);
echo "E:", $box->data, ";";
''',
        'expected_stdout': 'G;F:7;E:8;',
        'discriminator': 'A direct named reference Get keeps its real property CELL through the unchanged named receive path.',
    },
    {
        'id': 'named-value-argument-keeps-returned-array-copy',
        'source': '''<?php
function valueNamed326($row) { $row['x'] = 8; echo "F:", $row['x'], ";"; }
class ValueNamedGet326 implements ArrayAccess {
    public array $data = [['x' => 7]];
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return $this->data; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new ValueNamedGet326();
valueNamed326(row: $box['slot'][0]);
echo "E:", $box->data[0]['x'], ";";
''',
        'expected_stdout': 'G;F:8;E:7;',
        'discriminator': 'Named value arguments retain ordinary array COW and are excluded by the named reference writer source guard.',
    },
    {
        'id': 'named-reference-argument-captured-returned-row',
        'source': '''<?php
function namedRow18(&$row) { echo "F:", $row, ";"; $row = 8; }
class RefNamedRow18 implements ArrayAccess {
    public array $data = [7];
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return $this->data; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefNamedRow18();
namedRow18(row: $box['slot'][0]);
echo "E:", $box->data[0], ";";
''',
        'expected_stdout': 'G;F:7;E:8;',
        'discriminator': 'NAMED_SEND must authenticate the captured real row after the returned parent is released.',
    },
    {
        'id': 'nested-updates-captured-returned-row',
        'source': '''<?php
class RefUpdateRow18 implements ArrayAccess {
    public array $data = [7];
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return $this->data; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefUpdateRow18();
$old = $box['slot'][0]++;
$new = ++$box['slot'][0];
echo "E:", $old, ":", $new, ":", $box->data[0], ";";
''',
        'expected_stdout': 'G;G;E:7:9:9;',
        'discriminator': 'UPDATE_PREP must authenticate the live captured row and preserve pre/post results without Set.',
    },
    {
        'id': 'named-reference-duplicate-check-after-get-before-promotion',
        'source': '''<?php
function namedDuplicateRow18(&$row) { echo "wrongBody;"; $row = 99; }
class RefNamedDuplicateRow18 implements ArrayAccess {
    public array $data = [7];
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return $this->data; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefNamedDuplicateRow18();
$call18 = 'namedDuplicateRow18';
$given18 = 5;
try { $call18($given18, row: $box['slot'][0]); }
catch (Error $error18) { echo "X:", $error18->getMessage(), ";"; }
echo "E:", $box->data[0], ":", $given18, ";";
''',
        'expected_stdout': 'G;X:Named parameter $row overwrites previous argument;E:7:5;',
        'discriminator': 'The fetched real row must still pass NAMED_SEND name checks before promotion; a reference-task dispatch would bypass the duplicate error.',
    },
    {
        'id': 'nested-updates-preserve-copy-and-shared-embedded-alias',
        'source': '''<?php
$back18 = [7];
class RefUpdateAliasRow18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { global $back18; echo "G;"; return $back18; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefUpdateAliasRow18();
$copy18 = $back18;
$alias18 =& $back18[0];
$withAlias18 = $back18;
$old18 = $box['slot'][0]++;
$new18 = ++$box['slot'][0];
echo "E:", $old18, ":", $new18, ":", $back18[0], ":", $copy18[0], ":", $withAlias18[0], ":", $alias18, ";";
''',
        'expected_stdout': 'G;G;E:7:9:9:7:9:9;',
        'discriminator': 'Container COW preserves the earlier plain copy while the later embedded real row reference remains shared through pre/post updates.',
    },
]
