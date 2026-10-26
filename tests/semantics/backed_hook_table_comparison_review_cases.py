"""Normal raw backing-slot comparisons of cached hooked objects."""

CASES = {
    'virtual-first-default-live-setter': br'''<?php
class DefaultHookNumber127R {}
#[\AllowDynamicProperties]
class DefaultHookBox127R {
    public int $virtual {
        get { echo 'BAD|'; return 1000; }
    }
    protected $front;
    public int $value = 7 {
        get { echo 'BAD|'; return $this->value + 100; }
        set { echo 'S|'; $this->value = $value; }
    }
    public function init($front) { $this->front = $front; }
    public function changeFront() { $this->front = 1.0; }
    public function frontValue() { return $this->front; }
}
$left = new DefaultHookBox127R;
$right = new DefaultHookBox127R;
$left->init(0.0);
$right->init(new DefaultHookNumber127R);
$left->tag = 0;
$right->tag = 0;
$calls = 0;
set_error_handler(function ($level, $message) use ($left, $right, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class DefaultHookNumber127R could not be converted to float', '|';
    $left->changeFront();
    $right->value = 0;
    return false;
}, E_NOTICE);
echo 'B|';
$result = $left <= $right; // COMPARE
restore_error_handler();
echo 'R:', $result === false, ':', $left->frontValue() === 1.0, ':', $calls === 1, '|';
unset($left, $right);
echo 'A|';
''',
    'indirect-private-tail-inline-destructor': br'''<?php
class InlineHookNumber127R {}
class InlineHookVictim127R {
    public function __destruct() { echo 'D|'; }
}
#[\AllowDynamicProperties]
class InlineHookBox127R {
    public $front;
    public int $value = 7 {
        get { echo 'BAD|'; return $this->value + 100; }
    }
    private $tail;
    public function init($front, $tail) { $this->front = $front; $this->tail = $tail; }
    public function dropTail() { unset($this->tail); }
    public function hasTail() { return isset($this->tail); }
}
$left = new InlineHookBox127R;
$right = new InlineHookBox127R;
$left->init(new InlineHookNumber127R, 7);
$right->init(1, new InlineHookVictim127R);
$left->tag = 0;
$right->tag = 0;
$calls = 0;
set_error_handler(function ($level, $message) use ($right, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class InlineHookNumber127R could not be converted to int', '|';
    $right->dropTail();
    echo 'K|';
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left <=> $right; // COMPARE
restore_error_handler();
echo 'R:', $result === 1, ':', !$right->hasTail(), ':', $calls === 1, '|';
unset($left, $right);
echo 'A|';
''',
    'virtual-only-plain-equality': br'''<?php
class VirtualOnlyBox127R {
    public int $plain = 1;
    public int $virtual {
        get { echo 'BAD|'; return 1000; }
    }
}
$left = new VirtualOnlyBox127R;
$right = new VirtualOnlyBox127R;
$calls = 0;
set_error_handler(function ($level, $message) use (&$calls) {
    $calls = $calls + 1;
    echo 'BAD_NOTICE|';
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left == $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', $calls === 0, '|';
unset($left, $right);
echo 'A|';
''',
    'cached-count-skips-get-and-notice': br'''<?php
class CountHookNumber127R {}
#[\AllowDynamicProperties]
class CountHookBox127R {
    public int $virtual {
        get { echo 'BAD|'; return 1000; }
    }
    public $front;
    public int $value = 7 {
        get { echo 'BAD|'; return $this->value + 100; }
    }
    public function init($front) { $this->front = $front; }
}
$left = new CountHookBox127R;
$right = new CountHookBox127R;
$left->init(new CountHookNumber127R);
$right->init(1);
$left->tag = 0;
$right->tag = 0;
$right->extra = 0;
$calls = 0;
set_error_handler(function ($level, $message) use (&$calls) {
    $calls = $calls + 1;
    echo 'BAD_NOTICE|';
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left < $right; // COMPARE
restore_error_handler();
echo 'R:', $result === true, ':', $calls === 0, '|';
unset($left, $right);
echo 'A|';
''',
}

EXPECTED = {
    'virtual-first-default-live-setter': b'B|H:1|S|R:1:1:1|A|',
    'indirect-private-tail-inline-destructor': b'B|H:1|D|K|R:1:1:1|A|',
    'virtual-only-plain-equality': b'B|R:1:1|A|',
    'cached-count-skips-get-and-notice': b'B|R:1:1|A|',
}
