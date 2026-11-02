"""Original independently frozen nonpublic comparison witnesses."""
CASES = {
    'private-same-name-cache-owners': br"""<?php
class Base159 {
    private $same = 1;
    public function base($value): void { $this->same = $value; }
}
class Packet159 extends Base159 {
    private $same = 9;
    public $tail = 0;
    public function child($value): void { $this->same = $value; }
    public function __get($name) { echo 'BAD|'; return 0; }
}
function outer159($x): Exception { return new Exception('outer', 7); }
$left = new Packet159; $right = new Packet159; $right->base(2); $right->child(0);
$a = outer159($left); $b = outer159($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$left->base(2); echo 'C|', $a <=> $b, '|';
$view = (array)$left; $snapshot = $view; $view['extra'] = 99; $width = 0; foreach ($snapshot as $ignored) { $width = $width + 1; }
foreach ($left as $ignored) {} echo 'L|', $width, ':', $a <=> $b, '|';
foreach ($right as $ignored) {} echo 'T|', $a <=> $b, ':', $b <=> $a, '|';
$right->child(9); echo 'E|', $a <=> $b, '|';
$weak = WeakReference::create($left); $left = null; echo 'H|', (int)($weak->get() !== null), '|';
$a = null; echo 'D|', (int)($weak->get() === null), ':', $width, '|';
""",
    'protected-override-alias-recursion': br"""<?php
class Base159 {
    protected $first = 0;
    private $hidden = 0;
    public function bind(&$value): void { $this->first =& $value; }
    public function put($value): void { $this->first = $value; }
}
class Packet159 extends Base159 {
    protected $first = 0;
    private $tail = 0;
    public function tail($value): void { $this->tail = $value; }
    public function __get($name) { echo 'BAD|'; return 0; }
}
class Other159 { private int $uninitialized; }
function outer159($x): TypeError { return new TypeError('outer', 7); }
$left = new Packet159; $right = new Packet159; $live = [1]; $snapshot = $live;
$left->bind($live); $right->put([2]); $left->tail(9);
$a = outer159($left); $b = outer159($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
foreach ($left as $ignored) {} foreach ($right as $ignored) {} $view = (array)$left;
$snapshot[0] = 99; $live = [3]; echo 'C|', $snapshot[0], ':', $live[0], ':', $a <=> $b, '|';
$live = [2]; echo 'E|', $a <=> $b, '|';
$right->tail(9); echo 'Q|', $a <=> $b, '|';
$live = [$left]; $right->put([$right]); $hold = 'hold'; echo 'X|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; echo 'BAD|'; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$right->put([$left]); echo 'I|', $a <=> $b, ':', (int)($a == $b), '|';
$live = []; $right->put([]); $weak = WeakReference::create($left); $saved = $a->getTrace(); $a = null; $left = null;
echo 'H|', (int)($weak->get() !== null), '|';
$saved[0]['args'][0] = null; echo 'D|', (int)($weak->get() === null), '|';
$live = [4]; echo 'A|', $live[0], ':', $snapshot[0], '|';
$foreign = new Other159; $c = outer159($right); $d = outer159($foreign); echo 'K|', $c <=> $d, ':', $d <=> $c, '|';
""",
}
