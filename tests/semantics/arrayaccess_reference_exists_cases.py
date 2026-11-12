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
echo "I:", (int) isset($box['a']), ";";
echo "M:", (int) empty($box['b']), ";";
echo "C:", $box['c'] ?? 17, ";";
$box->present = false;
echo "i:", (int) isset($box['d']), ";";
echo "m:", (int) empty($box['e']), ";";
echo "c:", $box['f'] ?? 17, ";P:", (int) $box->present, ";";
''',
        'expected_stdout': 'I:E:a;1;M:E:b;G:b;0;C:E:c;G:c;11;i:E:d;0;m:E:e;1;c:E:f;17;P:0;',
    },
    {
        'id': 'mixed-local-result-demand',
        'source': '''<?php
class ReferenceExistsLocal implements ArrayAccess {
    public function &offsetExists($key): mixed { echo "E:", $key, ";"; return $key; }
    public function offsetGet($key): mixed { echo "G;"; return null; }
    public function offsetSet($key, $value): void {}
    public function offsetUnset($key): void {}
}
$box = new ReferenceExistsLocal();
echo "I:", (int) isset($box['0']), ":", (int) isset($box['on']), ";";
echo "M:", (int) empty($box['0']), ":", (int) empty($box['on']), ";";
echo "C:", $box['0'] ?? 17, ":", $box['on'] ?? 19, ";";
isset($box['on']);
empty($box['on']);
$box['on'] ?? 23;
echo "Z;";
''',
        'expected_stdout': 'I:E:0;0:E:on;1;M:E:0;1:E:on;G;1;C:E:0;17:E:on;G;19;E:on;E:on;G;E:on;G;Z;',
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
try { $saved = $box['x'] ?? 17; }
catch (Throwable $error) { echo "C:", $error->getMessage(), ";"; }
echo "S:", $saved, ";";
''',
        'expected_stdout': 'E;C:exists;S:3;',
    },
]
