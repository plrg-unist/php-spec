"""New VALUE-return Get originals; expectations await native/model agreement."""

CASES = [
    {
        'id': 'reference-get-value-return-warning-producer',
        'source': '''<?php
function valueReturnWarning18($level, $message, $file, $line) {
    echo "H:", $level, ";";
    return true;
}
set_error_handler('valueReturnWarning18');
class RefValueGet18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return false; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefValueGet18();
$box['slot'];
$box['slot']['x'][0] = 3;
echo "E;";
''',
        'expected_stdout': 'G;H:8;G;H:8;H:8192;E;',
        'discriminator': 'A mixed reference VALUE return needs the ordinary warning callback producer; implicit Get is demanded even when the outer read is discarded. It requires no typed return verification.',
    },
    {
        'id': 'reference-value-warning-throw-retires-computed-array-token',
        'source': '''<?php
class RefWarningToken18 { public function __destruct() { echo "D;"; } }
function refValueThrow18($level, $message, $file, $line) {
    echo "H:", $level, ";";
    throw new Exception('halt');
}
set_error_handler('refValueThrow18');
class RefValueThrowBox18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return [new RefWarningToken18()]; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefValueThrowBox18();
try { $box['slot']; }
catch (Exception $error18) { echo "X:", $error18->getMessage(), ";"; }
echo "E;";
''',
        'expected_stdout': 'G;H:8;D;X:halt;E;',
        'discriminator': 'The computed array owns its token through the Notice callback, then retires it before catch when that callback throws.',
    },
    {
        'id': 'reference-value-warning-handler-suspends-before-materialization',
        'source': '''<?php
function refValuePark18($level, $message, $file, $line) {
    echo "H:", $level, ";";
    if ($level === 8) { Fiber::suspend('return'); }
    return true;
}
set_error_handler('refValuePark18');
class RefValueParkBox18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return false; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefValueParkBox18();
$fiber18 = new Fiber(function () { global $box; $box['slot']['x'] = 3; echo "E;"; });
echo "A:", $fiber18->start(), ";";
$fiber18->resume();
echo "R;";
''',
        'expected_stdout': 'A:G;H:8;return;H:8192;E;R;',
        'discriminator': 'A genuine Fiber suspends inside the return Notice handler; after resumption the fresh reference is unwrapped and ordinary false-to-array handling remains ordered.',
    },
    {
        'id': 'reference-value-warning-keeps-return-opcode-file-and-line',
        'source': '''<?php
function refValueLocation18($level, $message, $file, $line) {
    global $line18;
    echo "H:", $level, ":", (int)($line === $line18), ":", (int)($file === __FILE__), ";";
    return true;
}
set_error_handler('refValueLocation18');
class RefValueLocationBox18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed {
        global $line18;
        echo "G;";
        $line18 = __LINE__ + 1;
        return false;
    }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefValueLocationBox18();
$box['slot'];
echo "E;";
''',
        'expected_stdout': 'G;H:8:1:1;E;',
        'discriminator': 'Notice callback location belongs to the actual RETURN_BY_REF statement, independently of the outer dimension or prior getter emission.',
    },
    {
        'id': 'untyped-computed-array-keeps-embedded-reference-through-notice',
        'source': '''<?php
$row329 = 7;
class RefValueToken329 { public function __destruct() { echo "D;"; } }
function refValueAlias329($level, $message, $file, $line) {
    global $row329;
    echo "H:", $level, ";";
    $row329 = 8;
    return true;
}
set_error_handler('refValueAlias329');
class RefValueAliasBox329 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $row329; echo "G;"; return [&$row329, new RefValueToken329()]; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box329 = new RefValueAliasBox329();
$copy329 = $box329['slot'];
echo "R:", $copy329[0], ";";
unset($copy329);
echo "E;";
''',
        'expected_stdout': 'G;H:8;R:8;D;E;',
        'discriminator': 'An untyped computed array survives the callback while its embedded real row cell remains shared; the token retires after the returned copy is unset.',
    },
    {
        'id': 'value-designated-raw-reference-observes-handler-write',
        'source': '''<?php
class RefValueWriteToken329 { public function __destruct() { echo "D;"; } }
$row329 = new RefValueWriteToken329();
function refValueWrite329($level, $message, $file, $line) {
    global $row329;
    echo "H:", $level, ";";
    $row329 = null;
    echo "Z;";
    return true;
}
set_error_handler('refValueWrite329');
class RefValueWriteBox329 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { global $out329, $row329; echo "G;"; return ($out329 =& $row329); }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box329 = new RefValueWriteBox329();
$box329['slot'];
echo "E:", (int)($row329 === null), ";";
''',
        'expected_stdout': 'G;H:8;D;Z;E:1;',
        'discriminator': 'A VALUE-designated returned reference owns its cell rather than the old token referent; writing that cell destroys the token inside the handler.',
    },
    {
        'id': 'value-designated-raw-reference-keeps-old-cell-after-rebind',
        'source': '''<?php
class RefValueRebindToken329 { public function __destruct() { echo "D;"; } }
$row329 = new RefValueRebindToken329();
$fresh329 = null;
function refValueRebind329($level, $message, $file, $line) {
    global $row329, $fresh329;
    echo "H:", $level, ";";
    unset($GLOBALS['out329']);
    $GLOBALS['row329'] =& $GLOBALS['fresh329'];
    echo "Z;";
    return true;
}
set_error_handler('refValueRebind329');
class RefValueRebindBox329 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { global $out329, $row329; echo "G;"; return ($out329 =& $row329); }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box329 = new RefValueRebindBox329();
$box329['slot'];
echo "E:", (int)($row329 === null), ";";
''',
        'expected_stdout': 'G;H:8;Z;D;E:1;',
        'discriminator': 'Rebinding the global name preserves the old captured return cell through the handler, so its token retires after Z and before the discarded read finishes.',
    },
    {
        'id': 'notice-handler-false-resumes-masked-default-once',
        'source': '''<?php
error_reporting(0);
function refValueFalse329($level, $message, $file, $line) { echo "H:", $level, ";"; return false; }
set_error_handler('refValueFalse329');
class RefValueFalseBox329 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return false; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box329 = new RefValueFalseBox329();
$box329['slot'];
echo "E;";
''',
        'expected_stdout': 'G;H:8;E;',
        'discriminator': 'A handler is invoked even with a masked Notice; false falls back once and then materializes the demanded Get result.',
    },
    {
        'id': 'reference-value-notice-throw-leaves-get-before-receiver-and-rv-release',
        'source': '''<?php
class GetLocal329 { public function __destruct() { echo "L;"; } }
class GetReturned329 { public function __destruct() { echo "D;"; } }
function getThrowRetire329($level, $message, $file, $line) {
    echo "H:", $level, ";";
    unset($GLOBALS['box329']);
    throw new Exception('halt');
}
set_error_handler('getThrowRetire329');
class GetThrowRetireBox329 implements ArrayAccess {
    public function __destruct() { echo "B;"; }
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed {
        echo "G;";
        $local329 = new GetLocal329();
        try { return [new GetReturned329()]; }
        catch (Exception $inside329) { echo "wrongInnerCatch;"; return false; }
    }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box329 = new GetThrowRetireBox329();
try { $box329['slot']; }
catch (Exception $outside329) { echo "X:", $outside329->getMessage(), ";"; }
echo "E;";
''',
        'expected_stdout': 'G;H:8;L;B;D;X:halt;E;',
        'discriminator': 'A throwing Notice handler removes the last ordinary receiver name; RETURN_BY_REF leaves Get without its inner catch, retires its local first, then the receiver and caller-owned returned temporary.',
    },
]
