"""Original append source bytes and preserved native observations.

OBSERVED_STDOUT records the original native run. Displayed diagnostics retain
the OBSERVED_FILES identity; a fresh differential run must use its own native
observation or explicitly substitute the filename.
"""

CASES = [
    ('intermediate-append-notice-rereads-rhs-after-root-retirement', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', ($key === null ? 'null' : $key), ';'; return [];  }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function () {
    global $rhs304;
    echo 'N;';
    $rhs304 = 9;
    unset($GLOBALS['root304']);
    return true;
});
$r304 = ($root304['root'][]['leaf'] = $rhs304);
restore_error_handler();
echo 'R:', $r304, ':', $rhs304, ':', (isset($root304) ? 1 : 0), ';';
'''),
    ('final-append-compound-uses-live-rhs-and-returned-temporary', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', ($key === null ? 'null' : $key), ';'; return [];  }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function () {
    global $rhs304;
    echo 'N;';
    $rhs304 = 9;
    unset($GLOBALS['root304']);
    return true;
});
$r304 = ($root304['root'][] += $rhs304);
restore_error_handler();
echo 'R:', $r304, ':', $rhs304, ':', (isset($root304) ? 1 : 0), ';';
'''),
    ('append-key-nested-compound-keeps-captured-null-offset', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', ($key === null ? 'null' : $key), ';'; return [];  }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function () {
    global $rhs304;
    echo 'N;';
    $rhs304 = 9;
    unset($GLOBALS['root304']);
    return true;
});
$r304 = ($root304[]['leaf'] += $rhs304);
restore_error_handler();
echo 'R:', $r304, ':', $rhs304, ':', (isset($root304) ? 1 : 0), ';';
'''),
    ('returned-child-append-get-null-keeps-real-consumer-owner', b'''<?php
class Child304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'C:', ($key === null ? 'null' : $key), ';'; return []; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { global $child304; echo 'P:', $key, ';'; return $child304; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$child304 = new Child304;
$root304 = new Append304;
$rhs304 = 4;
set_error_handler(function () {
    global $rhs304;
    echo 'N;';
    $rhs304 = 13;
    unset($GLOBALS['root304'], $GLOBALS['child304']);
    return true;
});
$r304 = ($root304['root'][]['leaf'] = $rhs304);
restore_error_handler();
echo 'R:', $r304, ':', $rhs304, ':', (isset($root304) ? 1 : 0), ':', (isset($child304) ? 1 : 0), ';';
'''),
    ('intermediate-append-throwing-notice-suppresses-missing-rhs', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', ($key === null ? 'null' : $key), ';'; return [];  }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function () {
    echo 'N;';
    unset($GLOBALS['root304']);
    throw new Error('notice304', 0, new Error('older304'));
});
try {
    $root304['root'][]['leaf'] = $missing304;
} catch (Error $e304) {
    echo 'C:', $e304->getMessage(), ':', $e304->getPrevious()->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ':', (isset($missing304) ? 1 : 0), ':', (isset($root304) ? 1 : 0), ';';
}
restore_error_handler();
'''),
    ('intermediate-append-computed-array-rhs-precedes-get-notice', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', ($key === null ? 'null' : $key), ';'; return [];  }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
function rhs304() { echo 'RHS;'; return [31]; }
$root304 = new Append304;
set_error_handler(function () {
    echo 'N;';
    unset($GLOBALS['root304']);
    return true;
});
$r304 = ($root304['root'][]['leaf'] = rhs304());
restore_error_handler();
echo 'R:', $r304[0], ':', (isset($root304) ? 1 : 0), ';';
'''),
    ('multiline-intermediate-append-get-throw-keeps-native-chain-and-lines', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; unset($GLOBALS['root304']); throw new Exception('get304', 0, new Exception('older304')); }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
$rhs304 = 4;
try {
    $r304 = ($root304[
        'root'
    ][][
        'leaf'
    ] = $rhs304);
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof Error ? 'Error' : 'Exception'), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    if ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ';';
        $q304 = $p304->getPrevious();
        if ($q304 !== null) { echo 'Q:', $q304->getMessage(), ':', $q304->getLine(), ';'; }
    }
    echo 'R:', $rhs304, ':', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
}
'''),
    ('multiline-child-null-key-append-get-throw-keeps-chain-and-lines', b'''<?php
class Child304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'C:', ($key === null ? 'null' : $key), ';'; unset($GLOBALS['root304'], $GLOBALS['child304']); throw new Exception('child304', 0, new Exception('older304')); }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { global $child304; echo 'P:', $key, ';'; return $child304; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$child304 = new Child304;
$root304 = new Append304;
$rhs304 = 4;
try {
    $r304 = ($root304[
        'root'
    ][][
        'leaf'
    ] = $rhs304);
} catch (Throwable $e304) {
    echo 'X:', ($e304 instanceof Error ? 'Error' : 'Exception'), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    if ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ';';
        $q304 = $p304->getPrevious();
        if ($q304 !== null) { echo 'Q:', $q304->getMessage(), ':', $q304->getLine(), ';'; }
    }
    echo 'R:', $rhs304, ':', (isset($root304) ? 1 : 0), ':', (isset($child304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
}
'''),
    ('intermediate-append-null-get-result-preserves-native-notice-and-error-kind', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return null; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function ($level304) {
    global $rhs304;
    echo 'H:', $level304, ';';
    $rhs304 = 9;
    unset($GLOBALS['root304']);
    return true;
});
try {
    $r304 = ($root304['root'][]['leaf'] = $rhs304);
    echo 'R:', $r304, ';';
} catch (Error $e304) {
    echo 'X:', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
}
restore_error_handler();
echo 'F:', $rhs304, ':', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('intermediate-append-false-get-result-preserves-native-notice-and-error-kind', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function ($level304) {
    global $rhs304;
    echo 'H:', $level304, ';';
    $rhs304 = 9;
    unset($GLOBALS['root304']);
    return true;
});
try {
    $r304 = ($root304['root'][]['leaf'] = $rhs304);
    echo 'R:', $r304, ';';
} catch (Error $e304) {
    echo 'X:', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
}
restore_error_handler();
echo 'F:', $rhs304, ':', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('intermediate-append-integer-get-result-preserves-native-notice-and-error-kind', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return 7; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function ($level304) {
    global $rhs304;
    echo 'H:', $level304, ';';
    $rhs304 = 9;
    unset($GLOBALS['root304']);
    return true;
});
try {
    $r304 = ($root304['root'][]['leaf'] = $rhs304);
    echo 'R:', $r304, ';';
} catch (Error $e304) {
    echo 'X:', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
}
restore_error_handler();
echo 'F:', $rhs304, ':', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('intermediate-append-string-get-result-preserves-native-notice-and-error-kind', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return 'x'; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function ($level304) {
    global $rhs304;
    echo 'H:', $level304, ';';
    $rhs304 = 9;
    unset($GLOBALS['root304']);
    return true;
});
try {
    $r304 = ($root304['root'][]['leaf'] = $rhs304);
    echo 'R:', $r304, ';';
} catch (Error $e304) {
    echo 'X:', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
}
restore_error_handler();
echo 'F:', $rhs304, ':', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('copied-real-row-append-keeps-old-cell-after-global-rebind-genuine-globals-target-singleton-detach-core-observers', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { global $data304; echo 'G:', $key, ';'; return $data304; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$old304 = ['old' => 5];
$new304 = ['replace' => 7];
$data304 = ['ref' => &$old304];
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function () {
    global $rhs304;
    echo 'N;';
    $GLOBALS['old304'] =& $GLOBALS['new304'];
    $rhs304 = 11;
    unset($GLOBALS['root304']);
    return true;
});
$r304 = ($root304['root']['ref'][]['leaf'] = $rhs304);
restore_error_handler();
echo 'R:', $r304, ':', $data304['ref']['old'], ':', (isset($data304['ref'][0]) ? 1 : 0), ':', $old304['replace'], ':', (isset($old304[0]) ? 1 : 0), ':', (isset($root304) ? 1 : 0), ';';
'''),
    ('copied-real-row-append-keeps-old-cell-after-global-rebind-genuine-globals-target-kept-real-row-core-observers', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { global $data304; echo 'G:', $key, ';'; return $data304; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$old304 = ['old' => 5];
$new304 = ['replace' => 7];
$data304 = ['ref' => &$old304];
$keep304 =& $old304;
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function () {
    global $rhs304;
    echo 'N;';
    $GLOBALS['old304'] =& $GLOBALS['new304'];
    $rhs304 = 11;
    unset($GLOBALS['root304']);
    return true;
});
$r304 = ($root304['root']['ref'][]['leaf'] = $rhs304);
restore_error_handler();
echo 'R:', $r304, ':', $data304['ref'][0]['leaf'], ':', $keep304[0]['leaf'], ':', $old304['replace'], ':', (isset($old304[0]) ? 1 : 0), ':', (isset($root304) ? 1 : 0), ';';
'''),
    ('double-intermediate-append-keeps-copied-real-row-after-rebind-genuine-globals-target-singleton-detach-core-observers', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { global $data304; echo 'G:', $key, ';'; return $data304; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$old304 = ['old' => 5];
$new304 = ['replace' => 7];
$data304 = ['ref' => &$old304];
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function () {
    global $rhs304;
    echo 'N;';
    $GLOBALS['old304'] =& $GLOBALS['new304'];
    $rhs304 = 17;
    unset($GLOBALS['root304']);
    return true;
});
$r304 = ($root304['root']['ref'][]['inner'][]['leaf'] = $rhs304);
restore_error_handler();
echo 'R:', $r304, ':', $data304['ref']['old'], ':', (isset($data304['ref'][0]) ? 1 : 0), ':', $old304['replace'], ':', (isset($old304[0]) ? 1 : 0), ':', (isset($root304) ? 1 : 0), ';';
'''),
    ('double-intermediate-append-keeps-copied-real-row-after-rebind-genuine-globals-target-kept-real-row-core-observers', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { global $data304; echo 'G:', $key, ';'; return $data304; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$old304 = ['old' => 5];
$new304 = ['replace' => 7];
$data304 = ['ref' => &$old304];
$keep304 =& $old304;
$rhs304 = 4;
$root304 = new Append304;
set_error_handler(function () {
    global $rhs304;
    echo 'N;';
    $GLOBALS['old304'] =& $GLOBALS['new304'];
    $rhs304 = 17;
    unset($GLOBALS['root304']);
    return true;
});
$r304 = ($root304['root']['ref'][]['inner'][]['leaf'] = $rhs304);
restore_error_handler();
echo 'R:', $r304, ':', $data304['ref'][0]['inner'][0]['leaf'], ':', $keep304[0]['inner'][0]['leaf'], ':', $old304['replace'], ':', (isset($old304[0]) ? 1 : 0), ':', (isset($root304) ? 1 : 0), ';';
'''),
    ('append-false-fetch-deprecated-throw-observes-late-rhs-boundary', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = ($root304['root'][]['leaf'] = $missing304);
} catch (Error $e304) {
    echo 'C:', $e304->getMessage(), ':', $e304->getPrevious()->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($missing304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-false-compound-deprecated-throw-observes-late-rhs-boundary', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = ($root304['root'][] += $missing304);
} catch (Error $e304) {
    echo 'C:', $e304->getMessage(), ':', $e304->getPrevious()->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($missing304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-false-divzero-replaces-pending-deprecated-with-full-chain', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] /= 0
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : 'Error'), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    if ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $q304 = $p304->getPrevious();
        if ($q304 !== null) {
            echo 'Q:', $q304->getMessage(), ':', $q304->getLine(), ':', ($q304->getFile() === __FILE__ ? 1 : 0), ';';
            $t304 = $q304->getPrevious();
            echo 'T:', ($t304 === null ? 0 : 1), ';';
        }
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-false-pending-handler-modulo-zero', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] %= 0
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-false-pending-handler-negative-shift', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] <<= -1
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-false-pending-handler-array-add-type-error', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] += [1]
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-false-pending-handler-array-concat-warning', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] .= [1]
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-false-pending-handler-power-zero-negative-deprecation', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] **= -1
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-pending-array-concat-reports-ineligible-warning', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
ini_set('display_errors', '1');
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
}, E_NOTICE | E_DEPRECATED);
try {
    $r304 = (
        $root304['root'][] .= [1]
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-pending-power-reports-after-handler-restoration', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
ini_set('display_errors', '1');
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        restore_error_handler();
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] **= -1
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-pending-leading-number-divide-aborts-before-zero', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] /= '0tail'
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-pending-float-modulo-aborts-before-zero', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] %= 0.5
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-pending-exact-float-modulo-aborts-before-zero', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] %= 0.0
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-pending-exact-float-string-modulo-reaches-zero', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] %= '0.0'
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-pending-ordinary-object-concat-preserves-error', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] .= new stdClass
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-pending-stringable-concat-skips-method-entirely', b'''<?php
class PendingString304 {
    public function __toString(): string {
        echo 'WRONG_STRING_CALL;';
        throw new Error('unexpected-string304');
    }
}
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] .= new PendingString304
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
    ('append-pending-throwable-concat-skips-internal-string-method', b'''<?php
class Append304 implements ArrayAccess {
    public function offsetExists(mixed $key): bool { echo 'E;'; return false; }
    public function offsetGet(mixed $key): mixed { echo 'G:', $key, ';'; return false; }
    public function offsetSet(mixed $key, mixed $value): void { echo 'S;'; }
    public function offsetUnset(mixed $key): void { echo 'U;'; }
}
$root304 = new Append304;
set_error_handler(function ($level304, $message304, $file304, $line304) {
    echo 'H:', $level304, ':', $line304, ';';
    unset($GLOBALS['root304']);
    if ($level304 === E_DEPRECATED) {
        throw new Error('deprecated304', 0, new Error('older304'));
    }
    return true;
});
try {
    $r304 = (
        $root304['root'][] .= new Exception('rhs304')
    );
} catch (Throwable $e304) {
    echo 'C:', ($e304 instanceof DivisionByZeroError ? 'DivisionByZeroError' : ($e304 instanceof ArithmeticError ? 'ArithmeticError' : 'Error')), ':', $e304->getMessage(), ':', $e304->getLine(), ':', ($e304->getFile() === __FILE__ ? 1 : 0), ';';
    $p304 = $e304->getPrevious();
    while ($p304 !== null) {
        echo 'P:', $p304->getMessage(), ':', $p304->getLine(), ':', ($p304->getFile() === __FILE__ ? 1 : 0), ';';
        $p304 = $p304->getPrevious();
    }
}
restore_error_handler();
echo 'F:', (isset($root304) ? 1 : 0), ':', (isset($r304) ? 1 : 0), ';';
'''),
]

OBSERVED_STDOUT = {'intermediate-append-notice-rereads-rhs-after-root-retirement': b'G:root;N;R:9:9:0;',
 'final-append-compound-uses-live-rhs-and-returned-temporary': b'G:root;N;R:9:9:0;',
 'append-key-nested-compound-keeps-captured-null-offset': b'G:null;N;N;R:9:9:0;',
 'returned-child-append-get-null-keeps-real-consumer-owner': b'P:root;C:null;N;R:13:13:0:0;',
 'intermediate-append-throwing-notice-suppresses-missing-rhs': b'G:root;N;C:notice304:older304:12'
                                                               b':1:0:0;',
 'intermediate-append-computed-array-rhs-precedes-get-notice': b'RHS;G:root;N;R:31:0;',
 'multiline-intermediate-append-get-throw-keeps-native-chain-and-lines': b'G:root;C:Exception:get30'
                                                                         b'4:4:1;P:older304:4;R:4:0'
                                                                         b':0;',
 'multiline-child-null-key-append-get-throw-keeps-chain-and-lines': b'P:root;C:null;X:Exception:ch'
                                                                    b'ild304:4:1;P:older304:4;R:4:'
                                                                    b'0:0:0;',
 'intermediate-append-null-get-result-preserves-native-notice-and-error-kind': b'G:root;H:8;R:9;F'
                                                                               b':9:0:1;',
 'intermediate-append-false-get-result-preserves-native-notice-and-error-kind': b'G:root;H:8;H:819'
                                                                                b'2;R:9;F:9:0:1;',
 'intermediate-append-integer-get-result-preserves-native-notice-and-error-kind': b'G:root;H:8;X'
                                                                                  b':Cannot use '
                                                                                  b'a scalar val'
                                                                                  b'ue as an arr'
                                                                                  b'ay:18:1;F:9:'
                                                                                  b'0:0;',
 'intermediate-append-string-get-result-preserves-native-notice-and-error-kind': b'G:root;H:8;X:[] '
                                                                                 b'operator not sup'
                                                                                 b'ported for strin'
                                                                                 b'gs:18:1;F:9:0:0;',
 'copied-real-row-append-keeps-old-cell-after-global-rebind-genuine-globals-target-singleton-detach-core-observers': b'G:ro'
                                                                                                                     b'ot;N'
                                                                                                                     b';R:1'
                                                                                                                     b'1:5:'
                                                                                                                     b'0:7:'
                                                                                                                     b'0:0;',
 'copied-real-row-append-keeps-old-cell-after-global-rebind-genuine-globals-target-kept-real-row-core-observers': b'G:ro'
                                                                                                                  b'ot;N'
                                                                                                                  b';R:1'
                                                                                                                  b'1:11'
                                                                                                                  b':11:'
                                                                                                                  b'7:0:'
                                                                                                                  b'0;',
 'double-intermediate-append-keeps-copied-real-row-after-rebind-genuine-globals-target-singleton-detach-core-observers': b'G:ro'
                                                                                                                         b'ot;N'
                                                                                                                         b';R:1'
                                                                                                                         b'7:5:'
                                                                                                                         b'0:7:'
                                                                                                                         b'0:0;',
 'double-intermediate-append-keeps-copied-real-row-after-rebind-genuine-globals-target-kept-real-row-core-observers': b'G:ro'
                                                                                                                      b'ot;N'
                                                                                                                      b';R:1'
                                                                                                                      b'7:17'
                                                                                                                      b':17:'
                                                                                                                      b'7:0:'
                                                                                                                      b'0;',
 'append-false-fetch-deprecated-throw-observes-late-rhs-boundary': b'G:root;H:8:18;H:8192:18;C:de'
                                                                   b'precated304:older304:13:1;F:'
                                                                   b'0:0:0;',
 'append-false-compound-deprecated-throw-observes-late-rhs-boundary': b'G:root;H:8:18;H:8192:18;'
                                                                      b'C:deprecated304:older304'
                                                                      b':13:1;F:0:0:0;',
 'append-false-divzero-replaces-pending-deprecated-with-full-chain': b'G:root;H:8:19;H:8192:19;C:Di'
                                                                     b'visionByZeroError:Division b'
                                                                     b'y zero:19:1;P:deprecated304:'
                                                                     b'13:1;Q:older304:13:1;T:0;F:0'
                                                                     b':0;',
 'append-false-pending-handler-modulo-zero': b'G:root;H:8:19;H:8192:19;C:DivisionByZeroError:Modulo'
                                             b' by zero:19:1;P:deprecated304:13:1;P:older304:13:1;F'
                                             b':0:0;',
 'append-false-pending-handler-negative-shift': b'G:root;H:8:19;H:8192:19;C:ArithmeticError:Bit sh'
                                                b'ift by negative number:19:1;P:deprecated304:13:1'
                                                b';P:older304:13:1;F:0:0;',
 'append-false-pending-handler-array-add-type-error': b'G:root;H:8:19;H:8192:19;C:Error:deprecat'
                                                      b'ed304:13:1;P:older304:13:1;F:0:0;',
 'append-false-pending-handler-array-concat-warning': b'G:root;H:8:19;H:8192:19;C:Error:deprecat'
                                                      b'ed304:13:1;P:older304:13:1;F:0:0;',
 'append-false-pending-handler-power-zero-negative-deprecation': b'G:root;H:8:19;H:8192:19;C:Error:'
                                                                 b'deprecated304:13:1;P:older304:13'
                                                                 b':1;F:0:0;',
 'append-pending-array-concat-reports-ineligible-warning': b'G:root;H:8:20;H:8192:20;\nWarning: Ar'
                                                           b'ray to string conversion in /home/us'
                                                           b'er/workspace/php-spec/.tools/arrayac'
                                                           b'cess-append-current-25/.tools/arraya'
                                                           b'ccess-append/native-33msdnxr/append-'
                                                           b'pending-array-concat-reports-ineligi'
                                                           b'ble-warning.php on line 20\nC:Error:d'
                                                           b'eprecated304:14:1;P:older304:14:1;F:'
                                                           b'0:0;',
 'append-pending-power-reports-after-handler-restoration': b'G:root;H:8:21;H:8192:21;\nDeprecated:'
                                                           b' Power of base 0 and negative expone'
                                                           b'nt is deprecated in /home/user/works'
                                                           b'pace/php-spec/.tools/arrayaccess-app'
                                                           b'end-current-25/.tools/arrayaccess-ap'
                                                           b'pend/native-33msdnxr/append-pending-'
                                                           b'power-reports-after-handler-restorat'
                                                           b'ion.php on line 21\nC:Error:deprecate'
                                                           b'd304:15:1;P:older304:15:1;F:0:0;',
 'append-pending-leading-number-divide-aborts-before-zero': b'G:root;H:8:19;H:8192:19;C:Error:depr'
                                                            b'ecated304:13:1;P:older304:13:1;F:0:0'
                                                            b';',
 'append-pending-float-modulo-aborts-before-zero': b'G:root;H:8:19;H:8192:19;C:Error:deprecated30'
                                                   b'4:13:1;P:older304:13:1;F:0:0;',
 'append-pending-exact-float-modulo-aborts-before-zero': b'G:root;H:8:19;H:8192:19;C:Error:deprecat'
                                                         b'ed304:13:1;P:older304:13:1;F:0:0;',
 'append-pending-exact-float-string-modulo-reaches-zero': b'G:root;H:8:19;H:8192:19;C:DivisionBy'
                                                          b'ZeroError:Modulo by zero:19:1;P:depr'
                                                          b'ecated304:13:1;P:older304:13:1;F:0:0;',
 'append-pending-ordinary-object-concat-preserves-error': b'G:root;H:8:19;H:8192:19;C:Error:depr'
                                                          b'ecated304:13:1;P:older304:13:1;F:0:0;',
 'append-pending-stringable-concat-skips-method-entirely': b'G:root;H:8:25;H:8192:25;C:Error:depr'
                                                           b'ecated304:19:1;P:older304:19:1;F:0:0;',
 'append-pending-throwable-concat-skips-internal-string-method': b'G:root;H:8:19;H:8192:19;C:Error:'
                                                                 b'deprecated304:13:1;P:older304:13'
                                                                 b':1;F:0:0;'}

OBSERVED_FILES = {'append-pending-array-concat-reports-ineligible-warning': '/home/user/workspace/php-spec/.tools/arrayaccess-append-current-25/.tools/arrayaccess-append/native-33msdnxr/append-pending-array-concat-reports-ineligible-warning.php',
 'append-pending-power-reports-after-handler-restoration': '/home/user/workspace/php-spec/.tools/arrayaccess-append-current-25/.tools/arrayaccess-append/native-33msdnxr/append-pending-power-reports-after-handler-restoration.php'}
