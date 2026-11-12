"""Ordinary scalar reference Get returns reuse the general CV verifier."""

CASES = [
    {
        'id': 'strict-float-cv-promotion',
        'source': '''<?php
declare(strict_types=1);
class ScalarFloatReferenceGet implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): float {
        echo "G:", $offset, ";";
        $value = $offset;
        return $value;
    }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}
$box = new ScalarFloatReferenceGet();
echo "R:", (int) ($box[17] === 17.0), ";";
$reference =& $box[23];
echo "A:", (int) ($reference === 23.0), ";";
$reference = "free";
echo "F:", $reference, ";";
echo "S:";
try { $box["29"]; } catch (TypeError $error) { echo "T;"; }
echo "Z;";
''',
        'expected_stdout': 'R:G:17;1;G:23;A:1;F:free;S:G:29;T;Z;',
    },
    {
        'id': 'weak-bool-and-literal-cv',
        'source': '''<?php
class WeakBoolReferenceGet implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): bool { $value = $offset; return $value; }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}

class LiteralTrueReferenceGet implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): true { $value = $offset; return $value; }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}

class LiteralFalseReferenceGet implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): false { $value = $offset; return $value; }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}
$bool = new WeakBoolReferenceGet();
echo "B:", (int) ($bool[2] === true), ":", (int) ($bool[0] === false), ";";
try { $bool[null]; } catch (TypeError $error) { echo "BT;"; }
$true = new LiteralTrueReferenceGet();
echo "T:", (int) ($true[true] === true), ";";
try { $true[1]; } catch (TypeError $error) { echo "TT;"; }
$false = new LiteralFalseReferenceGet();
echo "F:", (int) ($false[false] === false), ";";
try { $false[0]; } catch (TypeError $error) { echo "FT;"; }
echo "Z;";
''',
        'expected_stdout': 'B:1:1;BT;T:1;TT;F:1;FT;Z;',
    },
    {
        'id': 'weak-null-and-numeric-union-cv',
        'source': '''<?php
class LiteralNullReferenceGet implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): null { $value = $offset; return $value; }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}

class UnionNumericReferenceGet implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): int|float { $value = $offset; return $value; }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}

class NullableIntReferenceGet implements ArrayAccess {
    public function offsetExists($offset): bool { return true; }
    public function &offsetGet($offset): ?int { $value = $offset; return $value; }
    public function offsetSet($offset, $value): void {}
    public function offsetUnset($offset): void {}
}
$null = new LiteralNullReferenceGet();
echo "N:", (int) ($null[null] === null), ":", $null[null] ?? 17, ";";
try { $null[false]; } catch (TypeError $error) { echo "NT;"; }
$numeric = new UnionNumericReferenceGet();
echo "U:", (int) ($numeric["2"] === 2), ":", (int) ($numeric["2.5"] === 2.5), ";";
$nullable = new NullableIntReferenceGet();
echo "Q:", (int) ($nullable[null] === null), ":", (int) ($nullable["7"] === 7), ";Z;";
''',
        'expected_stdout': 'N:1:17;NT;U:1:1;Q:1:1;Z;',
    },
]
