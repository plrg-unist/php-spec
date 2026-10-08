<?php
class Operand353 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/dim-arrayaccess-throw-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/dim-arrayaccess-throw-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/dim-arrayaccess-throw-child.php' ? 'filename' : 'none'), '|';
        echo 'THROW|'; throw $e;
    }
}
class Rows353 implements ArrayAccess {
    public function offsetGet(mixed $key): mixed { echo 'GET-BAD|'; return 'BAD'; }
    public function offsetExists(mixed $key): bool { return true; }
    public function offsetSet(mixed $key, mixed $value): void { }
    public function offsetUnset(mixed $key): void { }
}
$rows353 = new Rows353; $key353 = 'before';
try { $value = include new Operand353; echo 'BAD|'; } catch (Throwable $e) { echo 'CAUGHT:', $e->getMessage(), '|'; }
echo 'END';
