"""Frozen nonpublic ordinary images; comparison must not call magic methods."""

CASES = {
    'nonpublic-inline-physical-severity': br'''<?php
interface Marker159 {}
class Base159 implements Marker159 {
    private int $base = 0;
    protected int $rank = 0;
    public int $tail = 0;
    public function base(int $value): void { $this->base = $value; }
    public function rank(int $value): void { $this->rank = $value; }
}
class Packet159 extends Base159 {
    private int $leaf = 0;
    protected int $rank = 0;
    public static $noise = 0;
    public function leaf(int $value): void { $this->leaf = $value; }
    public function __get($name) { echo 'BAD|'; return 0; }
    public function __toString(): string { echo 'BAD|'; return 'bad'; }
}
function outer159($x): Exception { return new Exception('outer', 7); }
function severe159($x): ErrorException { global $severity; return new ErrorException('outer', 7, $severity); }
$left = new Packet159; $right = new Packet159;
$left->base(1); $right->base(2); $left->rank(9); $right->rank(1); $left->tail = 9; $right->tail = 1; $left->leaf(9); $right->leaf(1);
$a = outer159($left); $b = outer159($right);
echo 'B|', $a <=> $b, ':', (int)($a == $b), ':', (int)($a != $b), ':', (int)($a < $b), ':', (int)($a <= $b), ':', (int)($a > $b), ':', (int)($a >= $b), ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
Packet159::$noise = NAN; echo 'N|', $a <=> $b, '|';
$left->base(2); echo 'R|', $a <=> $b, '|';
$left->rank(1); echo 'T|', $a <=> $b, '|';
$left->tail = 1; echo 'L|', $a <=> $b, '|';
$left->leaf(1); echo 'E|', $a <=> $b, '|';
$severity = 9; $c = severe159($left); $severity = 1; $d = severe159($right);
echo 'S|', $c <=> $d, ':', $d <=> $c, '|';
''',
    'nonpublic-typed-alias-owners': br'''<?php
class Packet159 {
    private array $data = [];
    protected array $tail = [];
    public function bind(array &$value): void { $this->data =& $value; }
    public function put(array $value): void { $this->data = $value; }
    public function tail(array $value): void { $this->tail = $value; }
    public function __get($name) { echo 'BAD|'; return 0; }
}
function outer159($x): ValueError { return new ValueError('outer', 7); }
$left = new Packet159; $right = new Packet159; $live = [1]; $snapshot = $live;
$left->bind($live); $right->put([2]); $left->tail([9]); $right->tail([1]);
$a = outer159($left); $b = outer159($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
foreach ($left as $ignored) {} foreach ($right as $ignored) {} $view = (array)$left;
$snapshot[0] = 99; $live = [3]; echo 'C|', $snapshot[0], ':', $live[0], ':', $a <=> $b, '|';
try { $live = 1; echo 'BAD|'; } catch (TypeError $e) { echo 'T|', get_class($e), ':', $live[0], '|'; }
$left->tail([]); $right->tail([]); $live = [2]; echo 'E|', $a <=> $b, '|';
$weak = WeakReference::create($left); $saved = $a->getTrace(); $a = null; $left = null;
echo 'H|', (int)($weak->get() !== null), '|';
$saved[0]['args'][0] = null; echo 'D|', (int)($weak->get() === null), '|';
$live = 5; echo 'R|', $live, ':', $snapshot[0], '|';
''',
    'nonpublic-uninitialized-control': br'''<?php
class Packet159 { private int $hidden; public $visible = 0; }
function outer159($x): Exception { return new Exception('outer', 7); }
$left = new Packet159; $right = new Packet159; $a = outer159($left); $b = outer159($right);
echo 'B|', $a <=> $b, '|';
''',
    'nonpublic-readonly-control': br'''<?php
readonly class Packet159 {
    private int $hidden;
    public function __construct(int $value) { $this->hidden = $value; }
}
function outer159($x): Exception { return new Exception('outer', 7); }
$left = new Packet159(1); $right = new Packet159(2); $a = outer159($left); $b = outer159($right);
echo 'B|', $a <=> $b, '|';
''',
}

EXPECTED = {
    'nonpublic-inline-physical-severity': b'B|-1:0:1:1:1:0:0:1|W|1:-1|N|-1|R|1|T|1|L|1|E|0|S|1:-1|',
    'nonpublic-typed-alias-owners': b'B|-1:1|C|99:3:1|T|TypeError:3|E|0|H|1|D|1|R|5:99|',
    'nonpublic-uninitialized-control': b'B|0|',
    'nonpublic-readonly-control': b'B|-1|',
}
