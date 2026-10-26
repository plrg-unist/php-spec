"""Independent normal-completion comparisons through non-public declared slots."""

CASES = {
    'private-table-live-numeric-reread': br'''<?php
class HiddenNumber124 {}
class HiddenBox124 {
    private $leaf;
    private $tail;
    public function init($value, $tail) { $this->leaf = $value; $this->tail = $tail; }
    public function update() { $this->leaf = 1; $this->tail = 7; }
    public function leaf() { return $this->leaf; }
}
$number = new HiddenNumber124;
$left = new HiddenBox124;
$right = new HiddenBox124;
$left->init($number, 7);
$right->init(0, 0);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($right, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class HiddenNumber124 could not be converted to int', '|';
    $right->update();
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left <=> $right; // COMPARE
restore_error_handler();
echo 'R:', $result === 0, ':', $right->leaf() === 1, ':', $calls === 1, '|';
unset($left, $right, $number);
echo 'A|';
''',
    'protected-table-retained-cell': br'''<?php
class ProtectedNumber124 {}
class ProtectedBox124 {
    protected $leaf;
    protected $tail;
    public function value($value, $tail) { $this->leaf = $value; $this->tail = $tail; }
    public function alias(&$value, $tail) { $this->leaf =& $value; $this->tail = $tail; }
    public function rebind(&$value) { $this->leaf =& $value; $this->tail = 7; }
    public function leaf() { return $this->leaf; }
}
$number = new ProtectedNumber124;
$left = new ProtectedBox124;
$right = new ProtectedBox124;
$opposite = 0;
$replacement = 9;
$left->value($number, 7);
$right->alias($opposite, 0);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($right, &$opposite, &$replacement, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class ProtectedNumber124 could not be converted to int', '|';
    $opposite = 1;
    $right->rebind($replacement);
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left == $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', $opposite === 1, ':', $right->leaf() === 9, ':', $calls === 1, '|';
unset($left, $right, $number, $opposite, $replacement);
echo 'A|';
''',
}

EXPECTED = {
    'private-table-live-numeric-reread': b'B|H:1|R:1:1:1|A|',
    'protected-table-retained-cell': b'B|H:1|R:1:1:1:1|A|',
}
