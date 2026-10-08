"""Independent 319 source proposals; execution credit belongs to separate reports."""

CASES = [
    {
        'id': 'shared-get-copy-and-nested-alias',
        'source': '''<?php
class RefCopy18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $data18; echo "G;"; return $data18; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$data18 = ['x' => 1, 'a' => []];
$box = new RefCopy18();
$copy = $box['slot'];
$box['slot']['x'] = 2;
echo "R:", $copy['x'], ":", $data18['x'], ";";
$box['slot']['a'][] = 3;
$ref =& $box['slot']['x'];
$ref = 7;
unset($box['slot']['a'][0]);
echo "E:", $copy['x'], ":", $data18['x'], ":", (int) isset($data18['a'][0]), ";";
''',
        'expected_stdout': 'G;G;R:1:2;G;G;G;E:1:7:0;',
        'discriminator': 'R copies the referent array; W/append/reference/Unset retain the shared returned CELL and do not call Set.',
    },
    {
        'id': 'get-rebinds-name-but-returns-old-cell',
        'source': '''<?php
class RefRebind18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) {
        global $back18, $fresh18;
        echo "G;";
        $selected =& $back18;
        $GLOBALS['back18'] =& $fresh18;
        return $selected;
    }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$back18 = [11];
$hold18 =& $back18;
$fresh18 = [31];
$box = new RefRebind18();
$box['slot'][] = 13;
echo "E:", $hold18[0], ":", $hold18[1], ":", $back18[0], ":", (int) isset($back18[1]), ";";
''',
        'expected_stdout': 'G;E:11:13:31:0;',
        'discriminator': 'The returned CELL is the original alias, independent of the rebound global name and the current source expression.',
    },
    {
        'id': 'sole-reference-direct-target-still-invalid',
        'source': '''<?php
class RefLocal18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { echo "G;"; $local = 4; return $local; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefLocal18();
try { $box['slot'] =& $missing18; }
catch (Error $error) { echo "X:", $error->getMessage(), ";"; }
echo "M:", (int) ($missing18 === null), ";";
''',
        'expected_stdout': 'G;X:Cannot assign by reference to an array dimension of an object;M:1;',
        'discriminator': 'A genuine sole-owner reference suppresses indirect Notice, unwraps to an owned VAR and remains an invalid ASSIGN_REF target; RHS acquisition still initializes missing18.',
    },
    {
        'id': 'compound-new-result-and-updates-share-cell',
        'source': '''<?php
class RefUpdate18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $number18; echo "G:", $number18, ";"; return $number18; }
    public function offsetSet($key, $value): void {
        global $number18;
        echo "S:", $number18, ":", $value, ";";
        $number18 = $value;
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$number18 = 5;
$box = new RefUpdate18();
$result = ($box['slot'] += 2);
echo "R:", $result, ";";
$before = $box['slot']++;
$after = ++$box['slot'];
echo "U:", $before, ":", $after, ":", $number18, ";";
''',
        'expected_stdout': 'G:5;S:5:7;R:7;G:7;G:8;U:7:9:9;',
        'discriminator': 'DIM_OP computes a separate result before Set observes the unchanged backing value; pre/post updates use the real CELL without Set.',
    },
    {
        'id': 'compound-reference-array-replaced-during-set',
        'source': '''<?php
error_reporting(0);
class RefArrayToken18 { public function __destruct() { echo "D;"; } }
class RefArrayLife18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $array18; echo "G;"; return $array18; }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        $GLOBALS['array18'] = null;
        echo "Z;";
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$array18 = [new RefArrayToken18()];
$box = new RefArrayLife18();
$box['slot'] .= 'b';
echo "E:", (int) ($array18 === null), ";";
''',
        'expected_stdout': 'G;S:Arrayb;D;Z;E:1;',
        'discriminator': 'DIM_OP scalar CONCAT drops its array input from the computed result. Replacing the real referenced array retires its child immediately inside Set.',
    },
    {
        'id': 'compound-reference-array-retained-after-name-rebind',
        'source': '''<?php
error_reporting(0);
class RefReboundArrayToken18 { public function __destruct() { echo "D;"; } }
class RefReboundArrayLife18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $array18; echo "G;"; return $array18; }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        $GLOBALS['array18'] =& $GLOBALS['other18'];
        echo "Z;";
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$other18 = null;
$array18 = [new RefReboundArrayToken18()];
$box = new RefReboundArrayLife18();
$box['slot'] .= 'b';
echo "E:", (int) ($array18 === null), ";";
''',
        'expected_stdout': 'G;S:Arrayb;Z;D;E:1;',
        'discriminator': 'The old CELL survives global name rebinding until the real DIM_OP Get rv releases after Set. The scalar result does not retain the array child.',
    },
    {
        'id': 'sole-reference-false-w-fetch-unwraps',
        'source': '''<?php
function noticeLocal18($level, $message, $file, $line) { echo "H:", $level, ";"; return true; }
set_error_handler('noticeLocal18');
class RefLocalFalse18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { echo "G;"; $local = false; return $local; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefLocalFalse18();
$box['slot']['x'][0] = 3;
echo "E;";
''',
        'expected_stdout': 'G;H:8192;E;',
        'discriminator': 'Explicit W unwrap makes the sole returned false a plain owned VAR; intermediate FETCH emits the false-to-array deprecation without indirect Notice.',
    },
    {
        'id': 'shared-reference-false-w-fetch-preserved',
        'source': '''<?php
function noticeShared18($level, $message, $file, $line) { echo "H:", $level, ";"; return true; }
set_error_handler('noticeShared18');
class RefSharedFalse18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $false18; echo "G;"; return $false18; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$false18 = false;
$box = new RefSharedFalse18();
$box['slot']['x'][0] = 3;
echo "V:", $false18['x'][0], ";E;";
''',
        'expected_stdout': 'G;V:3;E;',
        'discriminator': 'A shared reference retains its wrapper through intermediate FETCH; false initializes in place without deprecation and the backing CELL receives the deep write.',
    },
    {
        'id': 'unset-keeps-captured-child-after-parent-retirement',
        'source': '''<?php
function retireUnsetParent18($level, $message, $file, $line) {
    echo "H:", $level, ";";
    unset($GLOBALS['back18']);
    return true;
}
set_error_handler('retireUnsetParent18');
class RefUnsetParent18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) {
        global $back18;
        echo "G;";
        return $back18;
    }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$back18 = ['a' => [1 => 7, 2 => 9]];
$child18 =& $back18['a'];
$box = new RefUnsetParent18();
unset($box['slot']['a'][1.5]);
echo "E:", (int) isset($child18[1]), ":", $child18[2], ":", (int) isset($back18), ";";
''',
        'expected_stdout': 'G;H:8192;E:0:9:0;',
        'discriminator': 'The float-key handler retires the original Get backing parent; captured source metadata stays valid while the actual child alias and Unset temporary retain the selected table.',
    },
]
