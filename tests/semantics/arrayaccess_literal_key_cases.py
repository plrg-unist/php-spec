"""Originals for authenticated literal string keys in ArrayAccess consumers."""

CASES = [{'id': 'preserved-reference-exists-literal-keys',
  'source': '<?php\n'
            'class ReferenceExistsProperty implements ArrayAccess {\n'
            '    public $present = true;\n'
            '    #[ReturnTypeWillChange]\n'
            '    public function &offsetExists($key) { echo "E:", $key, ";"; return '
            '$this->present; }\n'
            '    public function offsetGet($key): mixed { echo "G:", $key, ";"; return 11; }\n'
            '    public function offsetSet($key, $value): void {}\n'
            '    public function offsetUnset($key): void {}\n'
            '}\n'
            '$box = new ReferenceExistsProperty();\n'
            'echo "I:", (int) isset($box[\'a\']), ";";\n'
            'echo "M:", (int) empty($box[\'b\']), ";";\n'
            'echo "C:", $box[\'c\'] ?? 17, ";";\n'
            '$box->present = false;\n'
            'echo "i:", (int) isset($box[\'d\']), ";";\n'
            'echo "m:", (int) empty($box[\'e\']), ";";\n'
            'echo "c:", $box[\'f\'] ?? 17, ";P:", (int) $box->present, ";";\n',
  'expected_stdout': 'I:E:a;1;M:E:b;G:b;0;C:E:c;G:c;11;i:E:d;0;m:E:e;1;c:E:f;17;P:0;'},
 {'id': 'read-set-compound-unset-literal-keys',
  'source': '<?php\n'
            'class LiteralKeyAccess implements ArrayAccess {\n'
            '    public function offsetExists($offset): bool { return true; }\n'
            '    public function offsetGet($offset): mixed { echo "G:", $offset, ";"; return 7; }\n'
            '    public function offsetSet($offset, $value): void { echo "S:", $offset, ":", '
            '$value, ";"; }\n'
            '    public function offsetUnset($offset): void { echo "U:", $offset, ";"; }\n'
            '}\n'
            '$box = new LiteralKeyAccess();\n'
            'echo "R:", $box[\'read\'], ";";\n'
            'echo "W:", ($box[\'write\'] = 3), ";";\n'
            'echo "M:", ($box[\'rw\'] += 2), ";";\n'
            "unset($box['gone']);\n"
            "$key = 'cv';\n"
            'echo "C:", $box[$key], ";Z;";\n',
  'expected_stdout': 'R:G:read;7;W:S:write:3;3;M:G:rw;S:rw:9;9;U:gone;C:G:cv;7;Z;'}]
