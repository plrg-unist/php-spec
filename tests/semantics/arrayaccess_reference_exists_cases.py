"""Scalar reference results from language-triggered offsetExists calls."""

CASES = [
    {
        'id': 'untyped-property-true-false',
        'source': '''<?php
class ReferenceExistsProperty implements ArrayAccess {
    public $present = true;
    #[ReturnTypeWillChange]
    public function &offsetExists($key) { echo "E:", $key, ";"; return $this->present; }
    public function offsetGet($key): mixed { echo "G:", $key, ";"; return 11; }
    public function offsetSet($key, $value): void {}
    public function offsetUnset($key): void {}
}
$box = new ReferenceExistsProperty();
echo "I:", (int) isset($box[1]), ";";
echo "M:", (int) empty($box[2]), ";";
echo "C:", $box[3] ?? 17, ";";
$box->present = false;
echo "i:", (int) isset($box[4]), ";";
echo "m:", (int) empty($box[5]), ";";
echo "c:", $box[6] ?? 17, ";P:", (int) $box->present, ";";
''',
        'expected_stdout': 'I:E:1;1;M:E:2;G:2;0;C:E:3;G:3;11;i:E:4;0;m:E:5;1;c:E:6;17;P:0;',
    },
    {
        'id': 'mixed-local-result-demand',
        'source': '''<?php
class ReferenceExistsLocal implements ArrayAccess {
    #[ReturnTypeWillChange]
    public function &offsetExists($key): mixed { echo "E:", $key, ";"; return $key; }
    public function offsetGet($key): mixed { echo "G;"; return null; }
    public function offsetSet($key, $value): void {}
    public function offsetUnset($key): void {}
}
$box = new ReferenceExistsLocal();
echo "I:", (int) isset($box[0]), ":", (int) isset($box[1]), ";";
echo "M:", (int) empty($box[0]), ":", (int) empty($box[1]), ";";
echo "C:", $box[0] ?? 17, ":", $box[1] ?? 19, ";";
isset($box[1]);
empty($box[1]);
$box[1] ?? 23;
echo "Z;";
''',
        'expected_stdout': 'I:E:0;0:E:1;1;M:E:0;1:E:1;G;1;C:E:0;17:E:1;G;19;E:1;E:1;G;E:1;G;Z;',
    },
    {
        'id': 'throw-skips-get-and-caller-store',
        'source': '''<?php
class ReferenceExistsThrow implements ArrayAccess {
    #[ReturnTypeWillChange]
    public function &offsetExists($key) { echo "E;"; throw new Exception('exists'); }
    public function offsetGet($key): mixed { echo "wrongGet;"; return 11; }
    public function offsetSet($key, $value): void {}
    public function offsetUnset($key): void {}
}
$box = new ReferenceExistsThrow();
$saved = 3;
try { $saved = $box[1] ?? 17; }
catch (Throwable $error) { echo "C:", $error->getMessage(), ";"; }
echo "S:", $saved, ";";
''',
        'expected_stdout': 'E;C:exists;S:3;',
    },
]
