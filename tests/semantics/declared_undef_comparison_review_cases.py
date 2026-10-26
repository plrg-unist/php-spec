"""Normal physical-UNDEF comparison witnesses, independent of pending throws."""

CASES = {
    'left-future-undefined-order': br'''<?php
class LeftUndefinedNumber125R {}
class LeftUndefinedBox125R {
    private $front;
    private $tail;
    public function init($front, $tail) { $this->front = $front; $this->tail = $tail; }
    public function dropTail() { unset($this->tail); }
    public function hasTail() { return isset($this->tail); }
}
$left = new LeftUndefinedBox125R;
$right = new LeftUndefinedBox125R;
$left->init(new LeftUndefinedNumber125R, 7);
$right->init(1, 0);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($left, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class LeftUndefinedNumber125R could not be converted to int', '|';
    $left->dropTail();
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left <=> $right; // COMPARE
restore_error_handler();
echo 'R:', $result === -1, ':', !$left->hasTail(), ':', $calls === 1, '|';
unset($left, $right);
echo 'A|';
''',
    'float-default-future-undefined': br'''<?php
class FloatUndefinedNumber125R {}
class FloatUndefinedBox125R {
    protected $front;
    protected $tail;
    public function init($front, $tail) { $this->front = $front; $this->tail = $tail; }
    public function dropTail() { unset($this->tail); }
    public function hasTail() { return isset($this->tail); }
}
$left = new FloatUndefinedBox125R;
$right = new FloatUndefinedBox125R;
$left->init(new FloatUndefinedNumber125R, 7);
$right->init(1.0, 0);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($left, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class FloatUndefinedNumber125R could not be converted to float', '|';
    $left->dropTail();
    return false;
}, E_NOTICE);
echo 'B|';
$result = $left <= $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', !$left->hasTail(), ':', $calls === 1, '|';
unset($left, $right);
echo 'A|';
''',
    'selected-alias-property-unset': br'''<?php
class SelectedAliasNumber125R {}
class SelectedAliasBox125R {
    protected $front;
    private $tail;
    public function value($front) { $this->front = $front; $this->tail = 7; }
    public function alias(&$front) { $this->front =& $front; $this->tail = 7; }
    public function dropFront() { unset($this->front); }
    public function hasFront() { return isset($this->front); }
}
$opposite = 0;
$left = new SelectedAliasBox125R;
$right = new SelectedAliasBox125R;
$left->value(new SelectedAliasNumber125R);
$right->alias($opposite);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($right, &$opposite, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class SelectedAliasNumber125R could not be converted to int', '|';
    $right->dropFront();
    $opposite = 1;
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left == $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', !$right->hasFront(), ':', $opposite === 1, ':', $calls === 1, '|';
unset($left, $right, $opposite);
echo 'A|';
''',
    'initial-typed-hole-filled': br'''<?php
class InitialHoleNumber125R {}
class InitialHoleBox125R {
    private $front;
    private int $tail;
    public function front($value) { $this->front = $value; }
    public function putTail($value) { $this->tail = $value; }
    public function readTail() { return $this->tail; }
}
$left = new InitialHoleBox125R;
$right = new InitialHoleBox125R;
$left->front(new InitialHoleNumber125R);
$right->front(1);
$right->putTail(7);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($left, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class InitialHoleNumber125R could not be converted to int', '|';
    $left->putTail(8);
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left > $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', $left->readTail() === 8, ':', $calls === 1, '|';
unset($left, $right);
echo 'A|';
''',
}

EXPECTED = {
    'left-future-undefined-order': b'B|H:1|R:1:1:1|A|',
    'float-default-future-undefined': b'B|H:1|R:1:1:1|A|',
    'selected-alias-property-unset': b'B|H:1|R:1:1:1:1|A|',
    'initial-typed-hole-filled': b'B|H:1|R:1:1:1|A|',
}
