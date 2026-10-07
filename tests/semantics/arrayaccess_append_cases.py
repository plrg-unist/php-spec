"""Original append source bytes and preserved native observations.

OBSERVED_STDOUT records the original native run. Displayed diagnostics retain
the OBSERVED_FILES identity; a fresh differential run must use its own native
observation or explicitly substitute the filename.
"""

CASES = [
    ('intermediate-append-leaf-computed-rhs-before-get', b'''<?php
error_reporting(0);
function rhs304() { echo 'I;'; return 13; }
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G:',$offset,';'; return $GLOBALS['data304']; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}

$data304=[]; $o304=new Outer304;
set_error_handler(function($n,$m) { echo 'N;'; unset($GLOBALS['o304']); return true; },8);
$r304=($o304[1][]['leaf']=rhs304());
restore_error_handler();
echo 'R:',$r304,':',(int)isset($data304[0]),':',(int)isset($o304),';';
'''),
    ('compound-append-rhs-and-original-array-change-at-notice', b'''<?php
error_reporting(0);
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G:',$offset,';'; return $GLOBALS['data304']; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}

$data304=[-2=>9]; $rhs304=11; $o304=new Outer304;
set_error_handler(function($n,$m) {
    echo 'N;'; $GLOBALS['rhs304']=17; $GLOBALS['data304'][-2]=23;
    unset($GLOBALS['o304']); return true;
},8);
$r304=($o304[1][]+=$rhs304);
restore_error_handler();
echo 'R:',$r304,':',$rhs304,':',$data304[-2],':',(int)isset($data304[0]),':',(int)isset($o304),';';
'''),
    ('intermediate-append-keeps-copied-real-row-after-alias-retirement', b'''<?php
error_reporting(0);
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G:',$offset,';'; return $GLOBALS['data304']; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}

$held304=9; $data304=[1=>&$held304]; $o304=new Outer304;
set_error_handler(function($n,$m) {
    echo 'N;'; $GLOBALS['held304']=11;
    unset($GLOBALS['held304'],$GLOBALS['o304']); return true;
},8);
$r304=($o304[1][]['leaf']=13);
restore_error_handler();
echo 'R:',$r304,':',$data304[1],':',(int)isset($data304[2]),':',(int)isset($held304),':',(int)isset($o304),';';
'''),
    ('outer-append-null-key-returned-child-compound', b'''<?php
error_reporting(0);
class Child304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed {
        echo 'C:',($offset===null?'N':$offset),';';
        $GLOBALS['rhs304']=17;
        return 5;
    }
    public function offsetSet(mixed $offset,mixed $value): void {
        echo 'S:',($offset===null?'N':$offset),':',$value,';';
        $GLOBALS['saved304']=$value;
    }
    public function offsetUnset(mixed $offset): void {}
}
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'O:',($offset===null?'N':$offset),';'; $inner=$GLOBALS['inner304']; unset($GLOBALS['inner304'],$GLOBALS['o304']); return $inner; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}

$inner304=new Child304; $o304=new Outer304; $rhs304=11;
set_error_handler(function($n,$m) { echo 'WRONGNOTICE;'; return true; },8);
$r304=($o304[][1]+=$rhs304);
restore_error_handler();
echo 'R:',$r304,':',$rhs304,':',$saved304,':',(int)isset($inner304),':',(int)isset($o304),';';
'''),
    ('child-append-compound-uses-null-key-and-sole-returned-object', b'''<?php
error_reporting(0);
class Child304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed {
        echo 'C:',($offset===null?'N':$offset),';';
        $GLOBALS['rhs304']=17;
        return 5;
    }
    public function offsetSet(mixed $offset,mixed $value): void {
        echo 'S:',($offset===null?'N':$offset),':',$value,';';
        $GLOBALS['saved304']=$value;
    }
    public function offsetUnset(mixed $offset): void {}
}
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'O:',($offset===null?'N':$offset),';'; $inner=$GLOBALS['inner304']; unset($GLOBALS['inner304'],$GLOBALS['o304']); return $inner; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}

$inner304=new Child304; $o304=new Outer304; $rhs304=11;
set_error_handler(function($n,$m) { echo 'WRONGNOTICE;'; return true; },8);
$r304=($o304[1][]+=$rhs304);
restore_error_handler();
echo 'R:',$r304,':',$rhs304,':',$saved304,':',(int)isset($inner304),':',(int)isset($o304),';';
'''),
    ('compound-append-thrown-notice-skips-late-undefined-rhs', b'''<?php
error_reporting(0);
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G:',$offset,';'; return $GLOBALS['data304']; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}

$data304=[]; $o304=new Outer304;
set_error_handler(function($n,$m) { echo 'N;'; unset($GLOBALS['o304']); throw new Exception('notice304'); },8);
try { $r304=($o304[1][]+=$missing304); } catch(Throwable $e) { echo 'C:',$e->getMessage(),';'; }
restore_error_handler();
echo 'R:',(int)isset($r304),':',(int)isset($missing304),':',(int)isset($data304[0]),':',(int)isset($o304),';';
'''),
    ('final-compound-get-null', b'''<?php
error_reporting(0);
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G:',$offset,';'; return null; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}
$rhs304=7; $o304=new Outer304;
set_error_handler(function($n,$m) {
    echo ($n===8?'N':($n===8192?'D':'X')),':',$m,';';
    $GLOBALS['rhs304']=13; unset($GLOBALS['o304']); return true;
});
try { $r304=($o304[1][] += $rhs304); }
catch(Throwable $e304) { echo 'C:',($e304 instanceof Error?'Error':'Exception'),':',$e304->getMessage(),';'; }
restore_error_handler();
echo 'R:',(isset($r304)?$r304:'unset'),':',$rhs304,':',(int)isset($o304),';';
'''),
    ('final-compound-get-false', b'''<?php
error_reporting(0);
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G:',$offset,';'; return false; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}
$rhs304=7; $o304=new Outer304;
set_error_handler(function($n,$m) {
    echo ($n===8?'N':($n===8192?'D':'X')),':',$m,';';
    $GLOBALS['rhs304']=13; unset($GLOBALS['o304']); return true;
});
try { $r304=($o304[1][] += $rhs304); }
catch(Throwable $e304) { echo 'C:',($e304 instanceof Error?'Error':'Exception'),':',$e304->getMessage(),';'; }
restore_error_handler();
echo 'R:',(isset($r304)?$r304:'unset'),':',$rhs304,':',(int)isset($o304),';';
'''),
    ('final-compound-get-int', b'''<?php
error_reporting(0);
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G:',$offset,';'; return 5; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}
$rhs304=7; $o304=new Outer304;
set_error_handler(function($n,$m) {
    echo ($n===8?'N':($n===8192?'D':'X')),':',$m,';';
    $GLOBALS['rhs304']=13; unset($GLOBALS['o304']); return true;
});
try { $r304=($o304[1][] += $rhs304); }
catch(Throwable $e304) { echo 'C:',($e304 instanceof Error?'Error':'Exception'),':',$e304->getMessage(),';'; }
restore_error_handler();
echo 'R:',(isset($r304)?$r304:'unset'),':',$rhs304,':',(int)isset($o304),';';
'''),
    ('final-compound-get-string', b'''<?php
error_reporting(0);
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'G:',$offset,';'; return 'abc'; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}
$rhs304=7; $o304=new Outer304;
set_error_handler(function($n,$m) {
    echo ($n===8?'N':($n===8192?'D':'X')),':',$m,';';
    $GLOBALS['rhs304']=13; unset($GLOBALS['o304']); return true;
});
try { $r304=($o304[1][] += $rhs304); }
catch(Throwable $e304) { echo 'C:',($e304 instanceof Error?'Error':'Exception'),':',$e304->getMessage(),';'; }
restore_error_handler();
echo 'R:',(isset($r304)?$r304:'unset'),':',$rhs304,':',(int)isset($o304),';';
'''),
    ('ordinary-undefined-cv-compound-append-callback-before-initialization', b'''<?php
$rhs304=7;
set_error_handler(function($level304) {
    echo 'H:',$level304,';';
    $GLOBALS['row304']=91; $GLOBALS['rhs304']=13;
    return true;
});
$r304=($row304[]+=$rhs304);
restore_error_handler();
echo 'R:',$r304,':',$row304[0],':',$rhs304,';';
'''),
    ('ordinary-false-reference-compound-append-retains-selected-table', b'''<?php
$row304=false; $old304=&$row304;
$replacement304=[4=>23]; $rhs304=7;
set_error_handler(function($level304) {
    echo 'H:',$level304,';';
    $GLOBALS['row304']=&$GLOBALS['replacement304'];
    $GLOBALS['rhs304']=13; return true;
});
$r304=($row304[]+=$rhs304);
restore_error_handler();
echo 'R:',$r304,':',$old304[0],':',$row304[4],':',(int)isset($row304[0]),':',$rhs304,';';
'''),
    ('ordinary-false-pending-append-stores-late-rhs', b'''<?php
$row304 = false;
$rhs304 = 7;
set_error_handler(function($level) {
    global $rhs304;
    echo "H:", $level, ";";
    $rhs304 = 13;
    throw new Error("pending304");
});
try { $result304 = $row304[] += $rhs304; }
catch (Throwable $error304) { echo "C:", $error304->getMessage(), ";"; }
restore_error_handler();
echo "R:", (int)isset($row304[0]), ":", $row304[0], ":", $rhs304, ":", (int)isset($result304), ";";
'''),
    ('ordinary-false-pending-array-concat-keeps-null-row', b'''<?php
$row304 = false;
set_error_handler(function($level) {
    echo "H:", $level, ";";
    throw new Error("pending304");
});
try { $result304 = $row304[] .= [1]; }
catch (Throwable $error304) { echo "C:", $error304->getMessage(), ";"; }
restore_error_handler();
echo "R:", (int)isset($row304[0]), ":", (int)($row304[0] === null), ":", (int)isset($result304), ";";
'''),
    ('ordinary-false-pending-global-cow-retires-selected-table', b'''<?php
$row304 = false;
set_error_handler(function($level) {
    echo "H:", $level, ";";
    $GLOBALS['row304'][9223372036854775807] = 9;
    throw new Error("pending304");
});
try { $result304 = $row304[] += $missing304; }
catch (Throwable $error304) {
    echo "C:", $error304::class, ":", $error304->getMessage(), ":", $error304->getLine(), ":", (int)($error304->getFile() === __FILE__), ";";
    echo "P:", (int)($error304->getPrevious() === null), ";";
}
restore_error_handler();
echo "R:", $row304[9223372036854775807], ":", (int)isset($row304[0]), ":", (int)isset($missing304), ":", (int)isset($result304), ";";
'''),
    ('child-explicit-null-compound-remains-dimension-task', b'''<?php
error_reporting(0);
class Child304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed {
        echo 'C:',($offset===null?'N':$offset),';';
        $GLOBALS['rhs304']=17;
        return 5;
    }
    public function offsetSet(mixed $offset,mixed $value): void {
        echo 'S:',($offset===null?'N':$offset),':',$value,';';
        $GLOBALS['saved304']=$value;
    }
    public function offsetUnset(mixed $offset): void {}
}
class Outer304 implements ArrayAccess {
    public function offsetExists(mixed $offset): bool { return false; }
    public function offsetGet(mixed $offset): mixed { echo 'O:',($offset===null?'N':$offset),';'; $inner=$GLOBALS['inner304']; unset($GLOBALS['inner304'],$GLOBALS['o304']); return $inner; }
    public function offsetSet(mixed $offset,mixed $value): void { echo 'OUTERSET;'; }
    public function offsetUnset(mixed $offset): void { echo 'OUTERUNSET;'; }
}

$inner304=new Child304; $o304=new Outer304; $rhs304=11;
set_error_handler(function($n,$m) { echo 'WRONGNOTICE;'; return true; },8);
$r304=($o304[1][null]+=$rhs304);
restore_error_handler();
echo 'R:',$r304,':',$rhs304,':',$saved304,':',(int)isset($inner304),':',(int)isset($o304),';';
'''),
]

OBSERVED_STDOUT = {'intermediate-append-leaf-computed-rhs-before-get': b'I;G:1;N;R:13:0:0;',
 'compound-append-rhs-and-original-array-change-at-notice': b'G:1;N;R:17:17:23:0:0;',
 'intermediate-append-keeps-copied-real-row-after-alias-retirement': b'G:1;N;R:13:11:0:0:0;',
 'outer-append-null-key-returned-child-compound': b'O:N;C:1;S:1:22;R:22:17:22:0:0;',
 'child-append-compound-uses-null-key-and-sole-returned-object': b'O:1;C:N;S:N:22;R:22:17:22:0:0;',
 'compound-append-thrown-notice-skips-late-undefined-rhs': b'G:1;N;C:notice304;R:0:0:0:0;',
 'final-compound-get-null': b'G:1;N:Indirect modification of overloaded element of Outer304 has no'
                            b' effect;R:13:13:0;',
 'final-compound-get-false': b'G:1;N:Indirect modification of overloaded element of Outer304 has no'
                             b' effect;D:Automatic conversion of false to array is deprecated;R:13:'
                             b'13:0;',
 'final-compound-get-int': b'G:1;N:Indirect modification of overloaded element of Outer304 has no'
                           b' effect;C:Error:Cannot use a scalar value as an array;R:unset:13:0;',
 'final-compound-get-string': b'G:1;N:Indirect modification of overloaded element of Outer304 ha'
                              b's no effect;C:Error:[] operator not supported for strings;R:unse'
                              b't:13:0;',
 'ordinary-undefined-cv-compound-append-callback-before-initialization': b'H:2;R:13:13:13;',
 'ordinary-false-reference-compound-append-retains-selected-table': b'H:8192;R:13:13:23:0:13;',
 'ordinary-false-pending-append-stores-late-rhs': b'H:8192;C:pending304;R:1:13:13:0;',
 'ordinary-false-pending-array-concat-keeps-null-row': b'H:8192;C:pending304;R:0:1:0;',
 'ordinary-false-pending-global-cow-retires-selected-table': b'H:8192;C:Error:pending304:6:1;P:1;R:'
                                                             b'9:0:0:0;',
 'child-explicit-null-compound-remains-dimension-task': b'O:1;C:N;S:N:22;R:22:17:22:0:0;'}

OBSERVED_FILES = {}
