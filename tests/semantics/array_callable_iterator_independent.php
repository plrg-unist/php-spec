<?php
class Base119 {
    public function take(&$x) {
        echo 'M|', $this->tag, '|', $x, '|';
        $x += 2;
        echo 'X|', $x, '|';
    }
}
class Old119 extends Base119 {
    public $tag = 'old';
    public function __destruct() { echo 'D|old|'; }
}
class New119 extends Base119 {
    public $tag = 'new';
    public function __destruct() { echo 'D|new|'; }
}
class I119 implements Iterator {
    private $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V|'; return $this->i === 0; }
    public function current(): mixed { echo 'C|'; return 3; }
    public function key(): mixed {
        global $cb, $owner;
        echo 'K|';
        $cb = [new New119, 'take'];
        $owner = null;
        return 0;
    }
    public function next(): void { echo 'N|'; ++$this->i; }
}
set_error_handler(function ($errno, $message) { echo 'W|', $message, '|'; });
$owner = new Old119;
$cb = [$owner, 'take'];
$it = new I119;
$cb(...$it);
echo 'A|';
$cb = null;
echo 'Z|';
