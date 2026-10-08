"""Originals for implicit Get demand, quiet reads, property cells and abrupt Set."""

CASES = [
    {
        'id': 'mixed-get-quiet-copy-and-unused-demand',
        'source': '''<?php
class RefQuiet19 implements ArrayAccess {
    public function offsetExists($key): bool { echo "X;"; return $key !== 'miss'; }
    public function &offsetGet($key): mixed { global $quiet19; echo "G;"; return $quiet19; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$quiet19 = ['x' => 3];
$box = new RefQuiet19();
$box['slot'];
$copy = $box['slot'];
$copy['x'] = 7;
$read = $box['slot'] ?? ['x' => 9];
$missing = $box['miss'] ?? 17;
$present = isset($box['slot']);
$absent = isset($box['miss']);
$empty = empty($box['slot']);
echo "R:", $copy['x'], ":", $quiet19['x'], ":", $read['x'], ":", $missing, ":", (int) $present, ":", (int) $absent, ":", (int) $empty, ";";
''',
        'expected_stdout': 'G;G;X;G;X;X;X;X;G;R:7:3:3:17:1:0:0;',
        'discriminator': 'Discarded R still demands Get; R/IS copy and dereference a shared array, while missing coalesce and isset do not call Get.',
    },
    {
        'id': 'mixed-get-keeps-property-reference-cell',
        'source': '''<?php
class RefProperty19 implements ArrayAccess {
    public array $row = ['x' => 4];
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return $this->row; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefProperty19();
$copy = $box['slot'];
$box['slot']['x'] = 7;
$box['slot'][] = 9;
echo "E:", $copy['x'], ":", $box->row['x'], ":", $box->row[0], ";";
''',
        'expected_stdout': 'G;G;G;E:4:7:9;',
        'discriminator': 'An accepted mixed Get preserves the real backed-property CELL and its array type source; copied R remains detached.',
    },
    {
        'id': 'compound-rebound-reference-retires-before-catch',
        'source': '''<?php
error_reporting(0);
class RefThrowToken19 { public function __destruct() { echo "D;"; } }
class RefThrow19 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    #[ReturnTypeWillChange]
    public function &offsetGet($key) { global $array19; echo "G;"; return $array19; }
    public function offsetSet($key, $value): void {
        echo "S:", $value, ";";
        $GLOBALS['array19'] =& $GLOBALS['other19'];
        throw new Exception('set');
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$other19 = null;
$array19 = [new RefThrowToken19()];
$box = new RefThrow19();
try { $box['slot'] .= 'b'; }
catch (Throwable $error) { echo "X:", $error->getMessage(), ";"; }
echo "E:", (int) ($array19 === null), ";";
''',
        'expected_stdout': 'G;S:Arrayb;D;X:set;E:1;',
        'discriminator': 'The raw returned CELL keeps the old array through throwing Set, then releases it before catch and preserves the original Exception.',
    },
    {
        'id': 'reference-sharing-tested-before-receiver-retirement',
        'source': '''<?php
function noticeReceiver19($level, $message, $file, $line) { echo "H:", $level, ";"; return true; }
set_error_handler('noticeReceiver19');
class RefReceiver19 implements ArrayAccess {
    public $data = false;
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed {
        echo "G;";
        unset($GLOBALS['box19']);
        return $this->data;
    }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "D;"; }
}
$box19 = new RefReceiver19();
$box19['slot']['x'][0] = 3;
echo "E;";
''',
        'expected_stdout': 'G;D;E;',
        'discriminator': 'W tests shared Get reference ownership before releasing the handler receiver; the now-singleton returned CELL keeps its wrapper and suppresses intermediate false conversion deprecation.',
    },
    {
        'id': 'reference-argument-keeps-captured-returned-row',
        'source': '''<?php
function rowArgument19(&$row) { echo "F:", $row, ";"; $row = 8; }
class RefArgument19 implements ArrayAccess {
    public $data = [7];
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed { echo "G;"; return $this->data; }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box19 = new RefArgument19();
rowArgument19($box19['slot'][0]);
echo "E:", $box19->data[0], ";";
''',
        'expected_stdout': 'G;F:7;E:8;',
        'discriminator': 'A by-reference parameter acquires the captured INDIRECT row after Get parent release and updates the original property-backed array.',
    },
    {
        'id': 'reference-get-parks-in-fiber-core-warning-handler',
        'source': '''<?php
function coreRefWarning18($level, $message, $file, $line) {
    global $box;
    echo "H:", $level, ";";
    $box['slot'][0] = 8;
    echo "E:", $box->data[0], ";";
    return true;
}
set_error_handler('coreRefWarning18');
class RefFiberCore18 implements ArrayAccess {
    public array $data = [7];
    public function offsetExists($key): bool { return true; }
    public function &offsetGet($key): mixed {
        echo "G;";
        Fiber::suspend('parked');
        return $this->data;
    }
    public function offsetSet($key, $value): void { echo "wrongSet;"; }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
}
$box = new RefFiberCore18();
$fiber = new Fiber('error_reporting');
echo "A:", $fiber->start(1.5), ";";
$fiber->resume();
echo "F:", $fiber->getReturn(), ";R:", error_reporting(), ";";
''',
        'expected_stdout': 'A:H:8192;G;parked;E:8;F:30719;R:30719;',
        'discriminator': 'The genuine Fiber error_reporting weak-receive warning keeps its core result through a handler and suspended mixed reference Get; resumed W writes the shared property CELL and main reporting is restored.',
    },
]
