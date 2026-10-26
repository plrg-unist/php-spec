#!/usr/bin/env python3
"""Original public-method Iterator-CV argument-unpack comparisons."""
from pathlib import Path
import function_scope as scope


CASES = {
    'selected-receiver': b'''<?php
class Receiver118 {
    public function __construct(public string $name) {}
    public function take($item) { echo "T|", $this->name, "|", $item, "|"; }
}
class SelectedIterator118 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { global $receiver; echo "K|"; $receiver = new Receiver118("new"); return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new Receiver118("old");
$iterator = new SelectedIterator118();
$receiver->take(...$iterator);
echo "A|", $receiver->name, "|";
''',
    'named-order': b'''<?php
class NamedReceiver118 {
    public function take($first, $second) { echo "T|", $first, "|", $second, "|"; }
}
class NamedIterator118 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 2; }
    public function current(): mixed { echo "C|"; return $this->index === 0 ? 22 : 11; }
    public function key(): mixed { echo "K|"; return $this->index === 0 ? "second" : "first"; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new NamedReceiver118();
$iterator = new NamedIterator118();
$receiver->take(...$iterator);
''',
    'byref-warning': b'''<?php
class ReferenceReceiver118 {
    public function take(&$item) { echo "T|", $item, "|"; $item = 9; }
}
class ReferenceIterator118 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
set_error_handler(static function ($severity, $message, $file, $line) {
    echo "H|", $severity, "|", $message, "|", $line, "|";
    return true;
});
$receiver = new ReferenceReceiver118();
$iterator = new ReferenceIterator118();
$receiver->take(...$iterator);
''',
    'invalid-key': b'''<?php
class InvalidReceiver118 {
    public function take($item) { echo "BAD|"; }
}
class InvalidIterator118 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { echo "K|"; return false; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new InvalidReceiver118();
$iterator = new InvalidIterator118();
try { $receiver->take(...$iterator); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";
''',
    'key-throw-receiver': b'''<?php
class ThrowReceiver118 {
    public function __construct(public string $name) {}
    public function take($item) { echo "BAD|"; }
}
class ThrowIterator118 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { global $receiver; echo "K|"; $receiver = new ThrowReceiver118("new"); throw new Exception("stop", 17); }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new ThrowReceiver118("old");
$iterator = new ThrowIterator118();
try { $receiver->take(...$iterator); }
catch (Exception $error) { echo "E|", $error->getCode(), "|", $receiver->name, "|"; }
''',
    'direct-function-control': b'''<?php
class ControlIterator118 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 8; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
function control118($item) { echo "T|", $item, "|"; }
$iterator = new ControlIterator118();
control118(...$iterator);
''',
}


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'method-iterator-unpack', Path(__file__), publish=False) else 1)
