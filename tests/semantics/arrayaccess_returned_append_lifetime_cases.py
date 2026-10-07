"""Independent Set-result lifetime originals and pinned native observations."""

CASES = [
    {
        'id': 'returned-child-unused-CV-result-must-not-pin-payload',
        'source': '''<?php
class PayloadUnused309 {
    public function __destruct() { echo 'P;'; }
}
class ChildUnused309 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'WRONGEXISTS;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'WRONGGET;'; return null; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S:', ($key === null ? 'N' : 'K'), ';'; }
    public function offsetUnset(mixed $key): void { echo 'WRONGUNSET;'; }
    public function __destruct() {
        echo 'C<;';
        unset($GLOBALS['rhsUnused309']);
        echo 'C>;';
    }
}
class OuterUnused309 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'WRONGEXISTS;'; return false; }
    public function offsetGet(mixed $key): mixed {
        echo 'G;';
        $heldUnused309 = $GLOBALS['childUnused309'];
        unset($GLOBALS['outerUnused309'], $GLOBALS['childUnused309']);
        return $heldUnused309;
    }
    public function offsetSet(mixed $key, mixed $value): void { echo 'WRONGOUTERSET;'; }
    public function offsetUnset(mixed $key): void { echo 'WRONGUNSET;'; }
}
$rhsUnused309 = new PayloadUnused309;
$childUnused309 = new ChildUnused309;
$outerUnused309 = new OuterUnused309;
$outerUnused309['root'][] = $rhsUnused309;
echo 'R;';
''',
    },
    {
        'id': 'returned-child-used-CV-result-retains-payload',
        'source': '''<?php
class PayloadUnused309 {
    public function __destruct() { echo 'P;'; }
}
class ChildUnused309 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'WRONGEXISTS;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'WRONGGET;'; return null; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S:', ($key === null ? 'N' : 'K'), ';'; }
    public function offsetUnset(mixed $key): void { echo 'WRONGUNSET;'; }
    public function __destruct() {
        echo 'C<;';
        unset($GLOBALS['rhsUnused309']);
        echo 'C>;';
    }
}
class OuterUnused309 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'WRONGEXISTS;'; return false; }
    public function offsetGet(mixed $key): mixed {
        echo 'G;';
        $heldUnused309 = $GLOBALS['childUnused309'];
        unset($GLOBALS['outerUnused309'], $GLOBALS['childUnused309']);
        return $heldUnused309;
    }
    public function offsetSet(mixed $key, mixed $value): void { echo 'WRONGOUTERSET;'; }
    public function offsetUnset(mixed $key): void { echo 'WRONGUNSET;'; }
}
$rhsUnused309 = new PayloadUnused309;
$childUnused309 = new ChildUnused309;
$outerUnused309 = new OuterUnused309;
$usedUnused309 = ($outerUnused309['root'][] = $rhsUnused309);
echo 'R;';
unset($usedUnused309);
''',
    },
    {
        'id': 'direct-child-unused-CV-result-must-not-pin-payload',
        'source': '''<?php
class PayloadDirectUnused309 {
    public function __destruct() { echo 'P;'; }
}
class ChildDirectUnused309 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'WRONGEXISTS;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'WRONGGET;'; return null; }
    public function offsetSet(mixed $key, mixed $value): void {
        echo 'S:', ($key === null ? 'N' : 'K'), ';';
        unset($GLOBALS['childDirectUnused309']);
    }
    public function offsetUnset(mixed $key): void { echo 'WRONGUNSET;'; }
    public function __destruct() {
        echo 'C<;';
        unset($GLOBALS['rhsDirectUnused309']);
        echo 'C>;';
    }
}
$rhsDirectUnused309 = new PayloadDirectUnused309;
$childDirectUnused309 = new ChildDirectUnused309;
$childDirectUnused309[] = $rhsDirectUnused309;
echo 'R;';
''',
    },
    {
        'id': 'returned-child-unused-computed-RHS-retires-before-owned-receiver',
        'source': '''<?php
function makeUnused309() { echo 'F;'; return new PayloadUnused309; }
class PayloadUnused309 {
    public function __destruct() { echo 'P;'; }
}
class ChildUnused309 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'WRONGEXISTS;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'WRONGGET;'; return null; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S:', ($key === null ? 'N' : 'K'), ';'; }
    public function offsetUnset(mixed $key): void { echo 'WRONGUNSET;'; }
    public function __destruct() {
        echo 'C<;';
        echo 'C>;';
    }
}
class OuterUnused309 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'WRONGEXISTS;'; return false; }
    public function offsetGet(mixed $key): mixed {
        echo 'G;';
        $heldUnused309 = $GLOBALS['childUnused309'];
        unset($GLOBALS['outerUnused309'], $GLOBALS['childUnused309']);
        return $heldUnused309;
    }
    public function offsetSet(mixed $key, mixed $value): void { echo 'WRONGOUTERSET;'; }
    public function offsetUnset(mixed $key): void { echo 'WRONGUNSET;'; }
}
$childUnused309 = new ChildUnused309;
$outerUnused309 = new OuterUnused309;
$outerUnused309['root'][] = makeUnused309();
echo 'R;';
''',
    },
]

OBSERVED_STDOUT = {
    'returned-child-unused-CV-result-must-not-pin-payload': b'G;S:N;C<;P;C>;R;',
    'returned-child-used-CV-result-retains-payload': b'G;S:N;C<;C>;R;P;',
    'direct-child-unused-CV-result-must-not-pin-payload': b'S:N;C<;P;C>;R;',
    'returned-child-unused-computed-RHS-retires-before-owned-receiver': b'F;G;S:N;P;C<;C>;R;',
}
