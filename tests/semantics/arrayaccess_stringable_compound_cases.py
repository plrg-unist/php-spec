"""New Stringable DIM_OP originals; expectations await native/model agreement."""

CASES = [
    {
        'id': 'compound-reference-referent-replaced-during-set',
        'source': '''<?php
class RefToken18 {
    public function __toString(): string { echo "T;"; return "a"; }
    public function __destruct() { echo "D;"; }
}
class RefLife18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $token18; echo "G;"; return $token18; }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        $GLOBALS['token18'] = null;
        echo "Z;";
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$token18 = new RefToken18();
$box = new RefLife18();
$box['slot'] .= 'b';
echo "E:", (int) ($token18 === null), ";";
''',
        'expected_stdout': 'G;T;S:ab;D;Z;E:1;',
        'discriminator': 'DIM_OP retains the real reference wrapper through Set; changing its referent can immediately retire the old object. A stale captured-left value adds an incorrect owner.',
    },
    {
        'id': 'compound-reference-old-cell-retained-after-name-rebind',
        'source': '''<?php
class RefReboundToken18 {
    public function __toString(): string { echo "T;"; return "a"; }
    public function __destruct() { echo "D;"; }
}
class RefReboundLife18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $token18; echo "G;"; return $token18; }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        $GLOBALS['token18'] =& $GLOBALS['other18'];
        echo "Z;";
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$other18 = null;
$token18 = new RefReboundToken18();
$box = new RefReboundLife18();
$box['slot'] .= 'b';
echo "E:", (int) ($token18 === null), ";";
''',
        'expected_stdout': 'G;T;S:ab;Z;D;E:1;',
        'discriminator': 'Rebinding the name leaves the old CELL referent alive until DIM_OP releases its genuine Get rv after Set; a copied/relooked-up result loses this lifetime.',
    },
    {
        'id': 'left-stringable-write-and-current-rhs-conversion',
        'source': '''<?php
class OldRight334 {
    public function __toString(): string { echo "wrongOld;"; return "old"; }
    public function __destruct() { echo "O;"; }
}
class NewRight334 { public function __toString(): string { echo "N;"; return "b"; } }
class LeftWrite334 {
    public function __toString(): string {
        echo "T;";
        $GLOBALS['token334'] = null;
        $GLOBALS['right334'] = new NewRight334();
        echo "Z;";
        return "a";
    }
    public function __destruct() { echo "D;"; }
}
class LeftWriteBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $token334; echo "G;"; return $token334; }
    public function offsetSet($key, $value): void { echo "S:", $value, ";"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$token334 = new LeftWrite334();
$right334 = new OldRight334();
$box334 = new LeftWriteBox334();
$box334['slot'] .= $right334;
echo "E:", (int)($token334 === null), ";";
''',
        'expected_stdout': 'G;T;O;Z;D;N;S:ab;E:1;',
        'discriminator': 'Left conversion protects its receiver only through the call, then converts the current RHS CV after replacing its old object.',
    },
    {
        'id': 'left-stringable-rebind-keeps-old-get-cell',
        'source': '''<?php
class LeftRebind334 {
    public function __toString(): string {
        echo "T;";
        $GLOBALS['token334'] =& $GLOBALS['other334'];
        echo "Z;";
        return "a";
    }
    public function __destruct() { echo "D;"; }
}
class LeftRebindBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $token334; echo "G;"; return $token334; }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ":", (int)($GLOBALS['token334'] === null), ";";
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$other334 = null;
$token334 = new LeftRebind334();
$box334 = new LeftRebindBox334();
$box334['slot'] .= 'b';
echo "E:", (int)($token334 === null), ";";
''',
        'expected_stdout': 'G;T;Z;S:ab:1;D;E:1;',
        'discriminator': 'Rebinding during conversion preserves the original Get reference through Set instead of resolving the new global entry.',
    },
    {
        'id': 'rhs-cv-stringable-write-retires-before-set',
        'source': '''<?php
class RightCv334 {
    public function __toString(): string {
        echo "T;";
        $GLOBALS['right334'] = null;
        echo "Z;";
        return "b";
    }
    public function __destruct() { echo "D;"; }
}
class RightCvBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $row334; echo "G;"; return $row334; }
    public function offsetSet($key, $value): void { echo "S:", $value, ";"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$row334 = 'a';
$right334 = new RightCv334();
$box334 = new RightCvBox334();
$result334 = ($box334['slot'] .= $right334);
echo "R:", $result334, ";E:", $row334, ":", (int)($right334 === null), ";";
''',
        'expected_stdout': 'G;T;Z;D;S:ab;R:ab;E:a:1;',
        'discriminator': 'An RHS CV is a live pointer and gains no stale object owner through Set; the cast receiver owner ends before Set.',
    },
    {
        'id': 'computed-rhs-stringable-keeps-op-data-owner-through-set',
        'source': '''<?php
class RightTemp334 {
    public function __toString(): string { echo "T;"; return "b"; }
    public function __destruct() { echo "D;"; }
}
class RightTempBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G;"; return 'a'; }
    public function offsetSet($key, $value): void { echo "S:", $value, ";"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box334 = new RightTempBox334();
$result334 = ($box334['slot'] .= new RightTemp334());
echo "R:", $result334, ";E;";
''',
        'expected_stdout': 'G;T;S:ab;D;R:ab;E;',
        'discriminator': 'A computed RHS owns its OP_DATA temporary through Set, independently of the transient cast receiver owner.',
    },
    {
        'id': 'left-conversion-throw-skips-set-and-retires-rv-before-receiver',
        'source': '''<?php
class ThrowingLeft334 {
    public function __toString(): string {
        echo "T;";
        unset($GLOBALS['box334']);
        throw new RuntimeException('convert');
    }
    public function __destruct() { echo "D;"; }
}
class ThrowingLeftBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G;"; return new ThrowingLeft334(); }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$box334 = new ThrowingLeftBox334();
try { $box334['slot'] .= 'b'; }
catch (RuntimeException $error334) { echo "X:", $error334->getMessage(), ";"; }
echo "E;";
''',
        'expected_stdout': 'G;T;D;B;X:convert;E;',
        'discriminator': 'Failed conversion suppresses Set and frees the owned by-value Get RV before the captured ArrayAccess receiver.',
    },
    {
        'id': 'set-throw-keeps-rebound-get-cell-until-rv-release',
        'source': '''<?php
class SetThrowToken334 {
    public function __toString(): string { echo "T;"; return "a"; }
    public function __destruct() { echo "D;"; }
}
class SetThrowBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $token334; echo "G;"; return $token334; }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        unset($GLOBALS['box334']);
        $GLOBALS['token334'] =& $GLOBALS['other334'];
        echo "Z;";
        throw new RuntimeException('set');
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$other334 = null;
$token334 = new SetThrowToken334();
$box334 = new SetThrowBox334();
try { $box334['slot'] .= 'b'; }
catch (RuntimeException $error334) { echo "X:", $error334->getMessage(), ";"; }
echo "E:", (int)($token334 === null), ";";
''',
        'expected_stdout': 'G;T;S:ab;Z;D;B;X:set;E:1;',
        'discriminator': 'Set failure preserves the old Get reference carrier and retires its referent before the captured receiver after a global-name rebind.',
    },
    {
        'id': 'stringable-cast-owner-survives-fiber-park-after-cell-write',
        'source': '''<?php
class ParkedLeft334 {
    public function __toString(): string {
        echo "T;";
        $GLOBALS['token334'] = null;
        echo "Z;";
        Fiber::suspend('parked');
        echo "Q;";
        return "a";
    }
    public function __destruct() { echo "D;"; }
}
class ParkedLeftBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { global $token334; echo "G;"; return $token334; }
    public function offsetSet($key, $value): void { echo "S:", $value, ";"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$token334 = new ParkedLeft334();
$box334 = new ParkedLeftBox334();
$fiber334 = new Fiber(function () {
    global $box334;
    $result334 = ($box334['slot'] .= 'b');
    echo "R:", $result334, ";";
});
$parked334 = $fiber334->start();
echo "P:", $parked334, ";";
$fiber334->resume();
echo "E:", (int)($token334 === null), ";";
''',
        'expected_stdout': 'G;T;Z;P:parked;Q;D;S:ab;R:ab;E:1;',
        'discriminator': 'A parked implicit cast retains its actual receiver after the backing cell is cleared, then releases that owner before Set on resume.',
    },
]

CASES += [
    {
        'id': 'byvalue-get-rv-retires-before-computed-rhs-and-receiver',
        'source': '''<?php
class LeftOwned334 {
    public function __toString(): string { echo "L;"; return "a"; }
    public function __destruct() { echo "D;"; }
}
class RightOwned334 {
    public function __toString(): string { echo "R;"; return "b"; }
    public function __destruct() { echo "Q;"; }
}
class OrderedBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G;"; return new LeftOwned334(); }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        unset($GLOBALS['box334']);
        echo "Z;";
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$box334 = new OrderedBox334();
$result334 = ($box334['slot'] .= new RightOwned334());
echo "R:", $result334, ";E;";
''',
        'expected_stdout': 'G;L;R;S:ab;Z;D;Q;B;R:ab;E;',
        'discriminator': 'Native DIM_OP releases its by-value Get RV before computed OP_DATA and the selected outer receiver, while preserving the used string result.',
    },
    {
        'id': 'right-conversion-throw-retires-get-rv-before-op-data-and-receiver',
        'source': '''<?php
class LeftBeforeThrow334 {
    public function __toString(): string { echo "L;"; return "a"; }
    public function __destruct() { echo "D;"; }
}
class RightThrow334 {
    public function __toString(): string {
        echo "R;";
        unset($GLOBALS['box334']);
        throw new RuntimeException('right');
    }
    public function __destruct() { echo "Q;"; }
}
class RightThrowBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G;"; return new LeftBeforeThrow334(); }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$box334 = new RightThrowBox334();
try { $box334['slot'] .= new RightThrow334(); }
catch (RuntimeException $error334) { echo "X:", $error334->getMessage(), ";"; }
echo "E;";
''',
        'expected_stdout': 'G;L;R;D;Q;B;X:right;E;',
        'discriminator': 'Right conversion failure skips Set, preserves its original exception and releases Get RV, OP_DATA and receiver in opcode order.',
    },
    {
        'id': 'set-key-cv-is-sampled-after-both-stringable-conversions',
        'source': '''<?php
class LeftKey334 {
    public function __toString(): string { echo "L;"; $GLOBALS['key334'] = 'left'; return "a"; }
}
class RightKey334 {
    public function __toString(): string { echo "R;"; $GLOBALS['key334'] = 'right'; return "b"; }
}
class KeyBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { global $token334; echo "G:", $key, ";"; return $token334; }
    public function offsetSet($key, $value): void { echo "S:", $key, ":", $value, ";"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$key334 = 'first';
$token334 = new LeftKey334();
$right334 = new RightKey334();
$box334 = new KeyBox334();
$box334[$key334] .= $right334;
echo "E;";
''',
        'expected_stdout': 'G:first;L;R;S:right:ab;E;',
        'discriminator': 'Set reads the original key CV pointer after both casts, rather than reusing the copied Get key or sampling before right conversion.',
    },
    {
        'id': 'plain-concat-control-retains-computed-result-after-set-mutations',
        'source': '''<?php
class PlainBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { global $row334; echo "G;"; $GLOBALS['right334'] = 'Z'; return $row334; }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        $GLOBALS['row334'] = false;
        $GLOBALS['right334'] = null;
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$row334 = 8;
$right334 = 'X';
$box334 = new PlainBox334();
$result334 = ($box334['slot'] .= $right334);
echo "R:", $result334, ";E:", (int)$row334, ":", (int)($right334 === null), ";";
''',
        'expected_stdout': 'G;S:8Z;R:8Z;E:0:1;',
        'discriminator': 'The shared CONCAT staging preserves ordinary nonobject direct DIM_OP, late RHS CV sampling and the computed used result.',
    },
    {
        'id': 'get-throw-retains-original-replacement-error-priority',
        'source': '''<?php
class GetThrowBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G;"; throw new RuntimeException('get'); }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
class UnenteredRight334 { public function __toString(): string { echo "wrongCast;"; return "b"; } }
$box334 = new GetThrowBox334();
try { $box334['slot'] .= new UnenteredRight334(); }
catch (Error $error334) { echo "X:", $error334->getMessage(), ":", $error334->getPrevious()->getMessage(), ";"; }
echo "E;";
''',
        'expected_stdout': 'G;X:Cannot use object of type GetThrowBox334 as array:get;E;',
        'discriminator': 'Get failure uses the existing opcode replacement Error with the original exception as previous; neither conversion nor Set begins.',
    },
    {
        'id': 'cast-receiver-destructor-throw-preserves-pending-exception',
        'source': '''<?php
class PendingCastRight334 {
    public function __toString(): string { echo "wrongRight;"; return "b"; }
}
class PendingCastLeft334 {
    public function __toString(): string {
        echo "T;";
        $GLOBALS['token334'] = null;
        unset($GLOBALS['box334']);
        echo "Z;";
        return "a";
    }
    public function __destruct() { echo "D;"; throw new RuntimeException('dtor'); }
}
class PendingCastBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $token334; echo "G;"; return $token334; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$token334 = new PendingCastLeft334();
$right334 = new PendingCastRight334();
$box334 = new PendingCastBox334();
try { $box334['slot'] .= $right334; }
catch (RuntimeException $error334) { echo "X:", $error334->getMessage(), ";"; }
echo "E:", (int)($token334 === null), ";";
''',
        'expected_stdout': 'G;T;Z;D;B;X:dtor;E:1;',
        'discriminator': 'Dropping the last cast receiver after a valid string return may throw; no later RHS cast or Set call enters with that pending exception.',
    },
]

CASES += [
    {
        'id': 'computed-key-normal-opcode-owner-order',
        'source': '''<?php
class CompoundKey334 { public function __destruct() { echo "K;"; } }
class CompoundLeft334 {
    public function __toString(): string { echo "L;"; return "a"; }
    public function __destruct() { echo "D;"; }
}
class CompoundRight334 {
    public function __toString(): string { echo "R;"; return "b"; }
    public function __destruct() { echo "Q;"; }
}
class CompoundKeyBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G;"; return new CompoundLeft334(); }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        unset($GLOBALS['box334']);
        echo "Z;";
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$box334 = new CompoundKeyBox334();
$result334 = ($box334[new CompoundKey334()] .= new CompoundRight334());
echo "R:", $result334, ";E;";
''',
        'expected_stdout': 'G;L;R;S:ab;Z;D;Q;B;K;R:ab;E;',
        'discriminator': 'Computed raw key adds no array-key coercion; it retires after the owned RV, computed RHS and selected outer receiver.',
    },
    {
        'id': 'computed-key-right-conversion-throw-owner-order',
        'source': '''<?php
class ThrowCompoundKey334 { public function __destruct() { echo "K;"; } }
class ThrowCompoundLeft334 {
    public function __toString(): string { echo "L;"; return "a"; }
    public function __destruct() { echo "D;"; }
}
class ThrowCompoundRight334 {
    public function __toString(): string {
        echo "R;";
        unset($GLOBALS['box334']);
        throw new RuntimeException('right');
    }
    public function __destruct() { echo "Q;"; }
}
class ThrowCompoundKeyBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G;"; return new ThrowCompoundLeft334(); }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$box334 = new ThrowCompoundKeyBox334();
try { $box334[new ThrowCompoundKey334()] .= new ThrowCompoundRight334(); }
catch (RuntimeException $error334) { echo "X:", $error334->getMessage(), ";"; }
echo "E;";
''',
        'expected_stdout': 'G;L;R;D;Q;B;K;X:right;E;',
        'discriminator': 'A conversion throw releases the raw RV, OP_DATA and outer receiver before the original computed key.',
    },
    {
        'id': 'computed-base-owner-survives-through-final-computed-key-release',
        'source': '''<?php
class ComputedLeft334 {
    public function __toString(): string { echo "L;"; return "a"; }
    public function __destruct() { echo "D;"; }
}
class ComputedRight334 {
    public function __toString(): string { echo "R;"; return "b"; }
    public function __destruct() { echo "Q;"; }
}
class ComputedKey334 { public function __destruct() { echo "K;"; } }
class ComputedBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G;"; return new ComputedLeft334(); }
    public function offsetSet($key, $value): void { echo "S:", $value, ";Z;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
function computedBox334() { return new ComputedBox334(); }
$result334 = (computedBox334()[new ComputedKey334()] .= new ComputedRight334());
echo "R:", $result334, ";E;";
''',
        'expected_stdout': 'G;L;R;S:ab;Z;D;Q;K;B;R:ab;E;',
        'discriminator': 'A computed OP1 owns the receiver independently of the inner/outer handler pins, so the receiver destructor runs after final OP2 key release.',
    },
    {
        'id': 'set-key-copy-retires-before-rv-when-original-cv-is-unset',
        'source': '''<?php
class KeyCopyLeft334 {
    public function __toString(): string { echo "L;"; return "a"; }
    public function __destruct() { echo "D;"; }
}
class KeyCopyRight334 {
    public function __toString(): string { echo "R;"; return "b"; }
    public function __destruct() { echo "Q;"; }
}
class KeyCopy334 { public function __destruct() { echo "K;"; } }
class KeyCopyBox334 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G;"; return new KeyCopyLeft334(); }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        unset($GLOBALS['key334']);
        unset($GLOBALS['box334']);
        echo "Z;";
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$key334 = new KeyCopy334();
$box334 = new KeyCopyBox334();
$result334 = ($box334[$key334] .= new KeyCopyRight334());
echo "R:", $result334, ";E;";
''',
        'expected_stdout': 'G;L;R;S:ab;Z;K;D;Q;B;R:ab;E;',
        'discriminator': 'The Set handler copy is the last key owner after a CV unset and releases before the raw Get RV; a computed key instead owns its OP2 until later.',
    },
]
