"""Independent normal comparisons of materialized non-public declared slots."""

CASES = {
    'private-shadow-physical-key': br'''<?php
class ShadowNumber124R {}
class ShadowBase124R {
    private $same;
    public function parentInit($value) { $this->same = $value; }
    public function parentValue() { return $this->same; }
}
class ShadowChild124R extends ShadowBase124R {
    private $same;
    public function childInit($value) { $this->same = $value; }
    public function childValue() { return $this->same; }
}
$number = new ShadowNumber124R;
$left = new ShadowChild124R;
$right = new ShadowChild124R;
$left->parentInit($number);
$left->childInit(0);
$right->parentInit(0);
$right->childInit(0);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($right, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class ShadowNumber124R could not be converted to int', '|';
    $right->childInit(1);
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left <=> $right; // COMPARE
restore_error_handler();
echo 'R:', $result === 1, ':', $right->parentValue() === 0, ':', $right->childValue() === 1, ':', $calls === 1, '|';
unset($left, $right, $number);
echo 'A|';
''',
    'protected-reversed-live-slots': br'''<?php
class ReverseNumber124R {}
class ReverseBox124R {
    protected $front;
    protected $tail;
    public function init($front, $tail) { $this->front = $front; $this->tail = $tail; }
    public function frontToOne() { $this->front = 1; }
    public function tailToSeven() { $this->tail = 7; }
    public function front() { return $this->front; }
    public function tail() { return $this->tail; }
}
$number = new ReverseNumber124R;
$left = new ReverseBox124R;
$right = new ReverseBox124R;
$left->init(2, 7);
$right->init($number, 0);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($left, $right, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class ReverseNumber124R could not be converted to int', '|';
    $left->frontToOne();
    $right->tailToSeven();
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left <= $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', $left->front() === 1, ':', $right->tail() === 7, ':', $calls === 1, '|';
unset($left, $right, $number);
echo 'A|';
''',
    'private-float-default-notice': br'''<?php
class FloatNumber124R {}
class FloatBox124R {
    private $leaf;
    public function init($value) { $this->leaf = $value; }
    public function update() { $this->leaf = 1.0; }
    public function leaf() { return $this->leaf; }
}
$number = new FloatNumber124R;
$left = new FloatBox124R;
$right = new FloatBox124R;
$left->init($number);
$right->init(0.5);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($right, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class FloatNumber124R could not be converted to float', '|';
    $right->update();
    return false;
}, E_NOTICE);
echo 'B|';
$result = $left == $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', $right->leaf() === 1.0, ':', $calls === 1, '|';
unset($left, $right, $number);
echo 'A|';
''',
    'protected-early-value-skips-notice': br'''<?php
class SkipNumber124R {}
class SkipBox124R {
    protected $first;
    protected $later;
    public function init($first, $later) { $this->first = $first; $this->later = $later; }
}
$number = new SkipNumber124R;
$left = new SkipBox124R;
$right = new SkipBox124R;
$left->init(1, $number);
$right->init(0, 1);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use (&$calls) {
    $calls = $calls + 1;
    echo 'UNEXPECTED|';
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left > $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', $calls === 0, '|';
unset($left, $right, $number);
echo 'A|';
''',
}

EXPECTED = {
    'private-shadow-physical-key': b'B|H:1|R:1:1:1:1|A|',
    'protected-reversed-live-slots': b'B|H:1|R:1:1:1:1|A|',
    'private-float-default-notice': b'B|H:1|R:1:1:1|A|',
    'protected-early-value-skips-notice': b'B|R:1:1|A|',
}
