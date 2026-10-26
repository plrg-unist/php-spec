"""Independent normal mixed declared/dynamic hash-table comparisons."""

CASES = {
    'left-copy-live-private-slot': br'''<?php
class LeftCopyNumber126R {}
#[\AllowDynamicProperties]
class LeftCopyBox126R {
    private $front;
    private $sentinel;
    public function init($front, $sentinel) { $this->front = $front; $this->sentinel = $sentinel; }
    public function equalize() { $this->sentinel = 1; }
    public function sentinel() { return $this->sentinel; }
}
$left = new LeftCopyBox126R;
$right = new LeftCopyBox126R;
$left->init(new LeftCopyNumber126R, 2);
$right->init(1, 1);
$left->tail = 2;
$right->tail = 3;
$calls = 0;
set_error_handler(function ($level, $message) use ($left, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class LeftCopyNumber126R could not be converted to int', '|';
    $left->tail = 9;
    $left->equalize();
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left <=> $right; // COMPARE
restore_error_handler();
echo 'R:', $result === -1, ':', $left->tail === 9, ':', $left->sentinel() === 1, ':', $calls === 1, '|';
unset($left, $right);
echo 'A|';
''',
    'right-copy-default-float': br'''<?php
class RightCopyNumber126R {}
#[\AllowDynamicProperties]
class RightCopyBox126R {
    protected $front;
    protected $sentinel;
    public function init($front, $sentinel) { $this->front = $front; $this->sentinel = $sentinel; }
    public function equalize() { $this->sentinel = 1; }
    public function sentinel() { return $this->sentinel; }
}
$left = new RightCopyBox126R;
$right = new RightCopyBox126R;
$left->init(new RightCopyNumber126R, 2);
$right->init(1.0, 1);
$left->tail = 2;
$right->tail = 3;
$calls = 0;
set_error_handler(function ($level, $message) use ($left, $right, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class RightCopyNumber126R could not be converted to float', '|';
    $right->tail = 1;
    $left->equalize();
    return false;
}, E_NOTICE);
echo 'B|';
$result = $left <= $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', $right->tail === 1, ':', $left->sentinel() === 1, ':', $calls === 1, '|';
unset($left, $right);
echo 'A|';
''',
    'old-table-cell-after-dynamic-unset': br'''<?php
class CellCopyNumber126R {}
#[\AllowDynamicProperties]
class CellCopyBox126R {
    private $front;
    public function init($front) { $this->front = $front; }
}
$outside = 0;
$left = new CellCopyBox126R;
$right = new CellCopyBox126R;
$left->init(new CellCopyNumber126R);
$right->init(1);
$left->tail =& $outside;
$right->tail = 9;
$calls = 0;
set_error_handler(function ($level, $message) use ($left, &$outside, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class CellCopyNumber126R could not be converted to int', '|';
    unset($left->tail);
    $outside = 9;
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left == $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', !isset($left->tail), ':', $outside === 9, ':', $calls === 1, '|';
unset($left, $right, $outside);
echo 'A|';
''',
    'count-shortcut-skips-notice': br'''<?php
class CountCopyNumber126R {}
#[\AllowDynamicProperties]
class CountCopyBox126R {
    protected $front;
    private $sentinel;
    public function init($front, $sentinel) { $this->front = $front; $this->sentinel = $sentinel; }
}
$left = new CountCopyBox126R;
$right = new CountCopyBox126R;
$left->init(new CountCopyNumber126R, 2);
$right->init(1, 1);
$left->tail = 2;
$right->tail = 3;
$right->extra = 0;
$calls = 0;
set_error_handler(function ($level, $message) use (&$calls) {
    $calls = $calls + 1;
    echo 'BAD|';
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left != $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', $calls === 0, ':', $left->tail === 2, '|';
unset($left, $right);
echo 'A|';
''',
}

EXPECTED = {name: b'B|H:1|R:1:1:1:1|A|' for name in CASES}
EXPECTED['count-shortcut-skips-notice'] = b'B|R:1:1:1|A|'
