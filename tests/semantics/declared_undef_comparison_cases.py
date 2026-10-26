"""Normal numeric-Notice callbacks clear physical declared slots."""

CASES = {
    'future-unset-inline-last-owner': br'''<?php
class UnsetNumber125 {}
class UnsetVictim125 {
    public function __destruct() { echo 'D|'; }
}
class FutureUnsetBox125 {
    private $front;
    private $tail;
    public function init($front, $tail) { $this->front = $front; $this->tail = $tail; }
    public function dropTail() { unset($this->tail); }
    public function hasTail() { return isset($this->tail); }
}
$left = new FutureUnsetBox125;
$right = new FutureUnsetBox125;
$left->init(new UnsetNumber125, 7);
$right->init(1, new UnsetVictim125);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($right, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class UnsetNumber125 could not be converted to int', '|';
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
    'both-unset-retained-reference-tail': br'''<?php
class SharedUnsetNumber125 {}
class SharedUnsetVictim125 {
    public function __destruct() { echo 'D|'; }
}
class SharedUnsetBox125 {
    private $front;
    private $tail;
    private $later;
    public function init($front, &$tail, $later) { $this->front = $front; $this->tail =& $tail; $this->later = $later; }
    public function dropTail() { unset($this->tail); }
    public function hasTail() { return isset($this->tail); }
}
$held = new SharedUnsetVictim125;
$left = new SharedUnsetBox125;
$right = new SharedUnsetBox125;
$left->init(new SharedUnsetNumber125, $held, 3);
$right->init(1, $held, 4);
foreach ($left as $unused) {}
foreach ($right as $unused) {}
$calls = 0;
set_error_handler(function ($level, $message) use ($left, $right, &$calls) {
    $calls = $calls + 1;
    echo 'H:', $level === E_NOTICE && $message === 'Object of class SharedUnsetNumber125 could not be converted to int', '|';
    $left->dropTail();
    $right->dropTail();
    echo 'K|';
    return true;
}, E_NOTICE);
echo 'B|';
$result = $left <=> $right; // COMPARE
restore_error_handler();
echo 'R:', $result === -1, ':', !$left->hasTail(), ':', !$right->hasTail(), ':', $calls === 1, '|';
unset($left, $right);
echo 'U|';
unset($held);
echo 'A|';
''',
}

EXPECTED = {
    'future-unset-inline-last-owner': b'B|H:1|D|K|R:1:1:1|A|',
    'both-unset-retained-reference-tail': b'B|H:1|K|R:1:1:1:1|U|D|A|',
}
