"""Fresh implicit Generator Get originals; predictions require native/model checks."""


def box():
    return '''class GeneratorGet344 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "wrongBody;"; yield 'ignored'; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
function computedBox344() { return new GeneratorGet344(); }
'''


compound = '''try { computedBox344()['k'] .= 'b'; }
catch (Error $error344) { echo "X:", $error344->getMessage(), ";"; }
echo "E;";
'''


CASES = [
    {
        'id': 'generator-get-byref-compound-unstarted',
        'source': '''<?php
class JoinGeneratorGetReview19 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "wrongBody;"; yield 'ignored'; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
function computedJoinBoxReview19() { return new JoinGeneratorGetReview19(); }
try { computedJoinBoxReview19()['k'] .= 'b'; }
catch (Error $errorReview19) { echo "X:", $errorReview19->getMessage(), ";"; }
echo "E;";
''',
        'expected_stdout': 'B;X:Object of class Generator could not be converted to string;E;',
        'discriminator': 'The Generator yield-reference flag still returns a known Generator value. The implicit Get body and Set remain unstarted before conversion fails.',
    },
    {
        'id': 'generator-get-value-compound-unstarted',
        'source': '<?php\n' + box() + compound,
        'expected_stdout': 'B;X:Object of class Generator could not be converted to string;E;',
        'discriminator': 'Ordinary Get creates its Generator eagerly but never starts its body for failed compound conversion; computed receiver cleanup precedes the catch.',
    },
    {
        'id': 'generator-get-escaped-key-and-receiver',
        'source': '''<?php
class GeneratorKey344 { public function __destruct() { echo "K;"; } }
class EscapedGeneratorGet344 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed {
        echo "G:", (int)(func_get_arg(0) === $key), ";";
        try { yield 7; }
        finally { echo "F;"; }
    }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$key344 = new GeneratorKey344();
$box344 = new EscapedGeneratorGet344();
$other344 = new EscapedGeneratorGet344();
$gen344 = $box344[$key344];
unset($box344, $key344);
echo "A;";
echo "C:", $gen344->current(), ";";
echo "U;";
unset($gen344);
echo "Z;";
unset($other344);
echo "E;";
''',
        'expected_stdout': 'A;C:G:1;7;U;F;K;B;Z;B;E;',
        'discriminator': 'The escaped Generator owns the received object key and receiver after both caller CVs disappear, retains its original argument view, and runs real paused-close finally cleanup.',
    },
    {
        'id': 'generator-get-discarded-fresh-owner-order',
        'source': '''<?php
class DiscardedGeneratorKey344 { public function __destruct() { echo "K;"; } }
''' + box() + '''computedBox344()[new DiscardedGeneratorKey344()];
echo "E;";
''',
        'expected_stdout': 'K;B;E;',
        'discriminator': 'An unused dimension still supplies a Get result; discarding the fresh Generator retires its real key and receiver without executing the body.',
    },
    {
        'id': 'generator-get-private-caller-inherited-method',
        'source': '''<?php
class ParentGeneratorGet344 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "G:", $key, ";"; yield 9; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
class ChildGeneratorGet344 extends ParentGeneratorGet344 {
    private function produce() { return $this['inside']; }
    public function create() { return $this->produce(); }
}
$box344 = new ChildGeneratorGet344();
$gen344 = $box344->create();
unset($box344);
echo "A;";
echo "C:", $gen344->current(), ";";
$gen344->next();
echo "Z;";
unset($gen344);
echo "E;";
''',
        'expected_stdout': 'A;C:G:inside;9;B;Z;E;',
        'discriminator': 'The effective public inherited Get keeps its declaring scope after the private source caller and outer caller have both returned.',
    },
    {
        'id': 'generator-get-reference-yield-api-snapshot',
        'source': '''<?php
class ReferenceGeneratorGet344 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed {
        echo "G;";
        $row344 = ['x' => 1];
        yield $row344;
        echo "Q:", $row344['x'], ";";
    }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$box344 = new ReferenceGeneratorGet344();
$gen344 = $box344['k'];
unset($box344);
echo "A;";
$snapshot344 = $gen344->current();
$snapshot344['x'] = 3;
foreach ($gen344 as &$value344) {
    $value344['x'] = 2;
    echo "V:", $snapshot344['x'], ";";
}
unset($value344, $snapshot344, $gen344);
echo "E;";
''',
        'expected_stdout': 'A;G;V:3;Q:2;B;E;',
        'discriminator': 'An implicit reference Generator Get emits no return-reference Notice; current returns a value snapshot while foreach binds the accepted328 live yield cell.',
    },
    {
        'id': 'generator-get-close-key-replaces-finally-exception',
        'source': '''<?php
class ThrowingGeneratorKey344 {
    public function __destruct() { echo "K;"; throw new Exception('key'); }
}
class ThrowingGeneratorGet344 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed {
        global $close344;
        echo "G;";
        try { yield 1; }
        finally { echo "F;"; throw $close344; }
    }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "B;"; }
}
$close344 = new Exception('close');
$key344 = new ThrowingGeneratorKey344();
$box344 = new ThrowingGeneratorGet344();
$gen344 = $box344[$key344];
unset($box344, $key344);
echo "A;";
echo "C:", $gen344->current(), ";";
try { echo "U;"; unset($gen344); }
catch (Exception $error344) {
    echo "X:", $error344->getMessage(), "/", $error344->getPrevious()->getMessage(), ":",
        (int)($error344->getPrevious()->getPrevious() === null), ";";
}
echo "E;";
''',
        'expected_stdout': 'A;C:G;1;U;F;K;B;X:key/close:1;E;',
        'discriminator': 'Paused close continues receiver cleanup after the key destructor replaces the precreated finally exception, then returns the replacement with the original as its sole previous exception. Precreation keeps the original exception trace from owning the Get key.',
    },
]
